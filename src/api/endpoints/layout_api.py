import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.api.schemas.layout import LayoutRequest, LayoutResponse
from src.services.layout_agent.models.layout_model import DynamicPPONetwork
from src.services.layout_agent.utils.layout_generator import generate_layout
from src.utils.markdown_parser import MarkdownParser
from src.utils.json_converter import layout_to_json
from src.utils.block_generator import BlockGenerator
from src.services.style_agent.models.style_model import StyleModel
from src.services.style_agent.rule_generator import StyleRuleGenerator
from src.services.style_agent.runtime.runtime_manager import RuntimeManager
from collections import namedtuple
from src.utils.config import STYLE_CONFIG
import torch
import os
from concurrent.futures import ThreadPoolExecutor

Block = namedtuple('Block', ['id', 'content_type', 'content_length', 'min_width', 'min_height'])

router = APIRouter()

# 全局变量声明
layout_model = None
style_model = None
rule_generator = None
runtime_manager = None
markdown_parser = None

current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
layout_model_path = os.path.join(current_dir, "data", "models", "layout", "layoutModel_05.pth")
style_model_path = os.path.join(current_dir, "data", "models", "style", "styleModel.pth")

# 初始化线程池
executor = ThreadPoolExecutor(max_workers=4)

def init_components():
    """初始化所有组件"""
    global layout_model, style_model, rule_generator, runtime_manager, markdown_parser
    
    # 初始化布局模型
    if layout_model is None:
        layout_model = DynamicPPONetwork()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        layout_model.load_state_dict(torch.load(layout_model_path, map_location=device))
        layout_model.eval()
    
    # # 初始化Markdown解析器
    if markdown_parser is None:
        markdown_parser = MarkdownParser()

@router.on_event("startup")
async def startup_event():
    """服务启动时初始化所有组件"""
    init_components()

@router.get("/health/check")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "components": {
            "layout_model": layout_model is not None,
            "style_model": style_model is not None,
            "rule_generator": rule_generator is not None,
            "runtime_manager": runtime_manager is not None,
            "markdown_parser": markdown_parser is not None
        }
    }
    

async def generate_layout_content(
    markdown_text: str,
    card_size: dict,
    theme_color: str,
    style_config: dict = STYLE_CONFIG
) -> dict:
    """
    生成布局内容的核心方法
    
    Args:
        markdown_text: Markdown文本内容
        card_size: 卡片尺寸配置 {"width": width, "height": height}
        theme_color: 主题颜色
        style_config: 样式配置
    
    Returns:
        dict: 包含布局信息的字典
    """
    # 解析markdown
    json_content = markdown_parser.parse_to_json(markdown_text)
    
    # 生成块
    generator = BlockGenerator(card_size, style_config)
    layout_infos, blocks = await execute_in_threadpool(generator.generate_blocks, json_content)
    
    # 如果有具体尺寸，生成布局
    if card_size.get('width') and card_size.get('height'):
        final_positions = await execute_in_threadpool(
            generate_layout,
            layout_model,
            card_size['width'],
            card_size['height'],
            blocks
        )
        layout_json = await execute_in_threadpool(
            generator.update_layout_and_get_content,
            json_content,
            layout_infos,
            final_positions,
            card_size['width']
        )
    else:
        layout_json = await execute_in_threadpool(
            generator.update_layout_and_get_content,
            json_content,
            layout_infos,
            blocks
        )
    
    # 生成样式规则
    generator = StyleRuleGenerator(
        layout_info=layout_json,
        card_size=card_size,
        theme_color=theme_color
    )
    style_rules = await execute_in_threadpool(generator.generate)
    
    return layout_json, style_rules


# 为请求设置并发限制
semaphore = asyncio.Semaphore(10)  # 最多处理10个并发任务

async def execute_in_threadpool(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args, **kwargs)

@router.post("/generate", response_model=LayoutResponse)
async def generate_layout_api(request: LayoutRequest):
    """生成布局和样式"""
    try:
        # 使用 Semaphore 控制并发
        async with semaphore:
            card_size = {
                
            }
            if request.card_width and request.card_height:
                card_size = {
                    "width": request.card_width-10,
                    "height": request.card_height
                }
            
            layout_json, style_rules = await generate_layout_content(
                request.markdown_text,
                card_size,
                request.theme_color
            )
            
            runtime = RuntimeManager(layout_info=layout_json, card_size=card_size, style_rules=style_rules)
            
            result = runtime.generate_html()

            return LayoutResponse(layout_json=result)
        
    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e)
            }
        )
        
@router.post("/generate/eight-elements", response_model=LayoutResponse)
async def generate_layout_eight_elements(request: LayoutRequest):
    """生成八要素布局"""
    try:
        # 使用 Semaphore 控制并发
        async with semaphore:
            card_size = {}
            if request.card_width and request.card_height:
                card_size = {
                    "width": int(request.card_width),
                    "height": int(request.card_height)
                }
                     
            layout_json, style_rules = await generate_layout_content(
                request.markdown_text,
                card_size,
                request.theme_color
            )
            
            runtime = RuntimeManager(layout_info=layout_json, card_size=card_size, style_rules=style_rules)
            
            result = runtime.generate_eight_element()
            
            return LayoutResponse(layout_json=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e)
            }
        )
            
def  handle_default_layout(request):
    return request

