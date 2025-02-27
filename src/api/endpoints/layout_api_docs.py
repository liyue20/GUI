# src/api/endpoints/layout_api.py
# 单线程文件
import json
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
import random

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

def init_components():
    """初始化所有组件"""
    global layout_model, style_model, rule_generator, runtime_manager, markdown_parser
    
    # 初始化布局模型
    if layout_model is None:
        layout_model = DynamicPPONetwork()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        layout_model.load_state_dict(torch.load(layout_model_path, map_location=device))
        layout_model.eval()
    
    # # 初始化样式模型
    # if style_model is None:
    #     style_model = StyleModel()
    #     style_model.load(style_model_path)
    
    # # 初始化规则生成器
    # if rule_generator is None:
    #     rule_generator = StyleRuleGenerator()
    
    # # 初始化运行时管理器
    # if runtime_manager is None:
    #     runtime_manager = RuntimeManager()
    
    # 初始化Markdown解析器
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

@router.post("/generate", response_model=LayoutResponse)
async def generate_layout_api(request: LayoutRequest):
    """生成布局和样式"""
    try:
        if not request.card_width or not request.card_height:
            # 这里实现默认的处理流程
            json_content = markdown_parser.parse_to_json(request.markdown_text)
            generator = BlockGenerator({}, STYLE_CONFIG)
            layout_infos, blocks = generator.generate_blocks(json_content)
            layout_json = generator.update_layout_and_get_content(json_content, layout_infos, blocks)
            generator = StyleRuleGenerator(layout_info = json_content, card_size= {}, theme_color=request.theme_color)
            style_rules = generator.generate()
            runtime = RuntimeManager(layout_info = layout_json, card_size={}, style_rules=style_rules)
            html = runtime.generate_html()
            return LayoutResponse(layout_json = html)
        else: 
            # 如果宽高都有值，执行原有流程
            card_width = int(request.card_width)
            card_height = int(request.card_height)
            # 1. 使用Markdown解析器处理输入
            generator = BlockGenerator({'width':card_width, 'height':card_height}, STYLE_CONFIG)
            json_content = markdown_parser.parse_to_json(request.markdown_text)
            layout_infos, blocks = generator.generate_blocks(json_content)

            # 2. 生成布局
            final_positions = generate_layout(
                layout_model, 
                card_width, 
                card_height, 
                blocks
            )
            container_width=int(request.card_width)
            # 4. 获取完整布局JSON
            layout_json = generator.update_layout_and_get_content(json_content, layout_infos, final_positions,container_width)
            # 保存 layout_json 到文件
            output_json_path = "layout_output.json"
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(layout_json, f, indent=4, ensure_ascii=False)
            card_size = {
                "width": card_width,
                "height": card_height
            }
            
            # 5. 优化样式
            generator = StyleRuleGenerator(
                layout_info=layout_json,
                card_size=card_size,
                theme_color=request.theme_color
            )

            style_rules = generator.generate()
            

            runtime = RuntimeManager(
                layout_info=layout_json,
                card_size=card_size,
                style_rules=style_rules
            )

            html = runtime.generate_html()
            # 将生成的 HTML 保存到本地文件
            output_dir = "output_html"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_file_path = os.path.join(output_dir, "generated_layout.html")
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(html)            
            # 7. 返回结果
            return LayoutResponse(layout_json = html)
        
    except Exception as e:
        # logger.error(f"Error in generate_layout_api: {str(e)}")
        # raise HTTPException(status_code=500, detail=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e)
            }
        )
    
def  handle_default_layout(request):
    return request