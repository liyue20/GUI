
#本地调试使用
import json
import os
import torch
import sys
# 确保 src 目录在 sys.path 中，放在最前面
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


from collections import namedtuple
from src.api.schemas.layout import LayoutRequest, LayoutResponse
from src.services.layout_agent.models.layout_model import DynamicPPONetwork
from src.services.layout_agent.utils.layout_generator import generate_layout
from src.utils.markdown_parser import MarkdownParser
from src.utils.block_generator import BlockGenerator
from src.services.style_agent.rule_generator import StyleRuleGenerator
from src.services.style_agent.runtime.runtime_manager import RuntimeManager
from src.utils.config import STYLE_CONFIG

# 定义 Block
Block = namedtuple('Block', ['id', 'content_type', 'content_length', 'min_width', 'min_height'])

# 全局变量
layout_model = None
markdown_parser = None

# 路径设置
current_dir = os.path.dirname(os.path.abspath(__file__))
layout_model_path = r'D:\songql2\liyue_01\data\models\layout\layoutModel_05.pth'

# 初始化组件
def init_components():
    """初始化布局模型和Markdown解析器"""
    global layout_model, markdown_parser

    # 初始化布局模型
    if layout_model is None:
        layout_model = DynamicPPONetwork()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #layout_model.load_state_dict(torch.load(layout_model_path, map_location=device))
        layout_model.load_state_dict(torch.load(layout_model_path, map_location=device, weights_only=True))
        layout_model.eval()

    # 初始化Markdown解析器
    if markdown_parser is None:
        markdown_parser = MarkdownParser()

def generate_layout_local(request: LayoutRequest):
    """本地生成布局和样式"""
    try:
        # 初始化
        init_components()

        # 输入卡片宽高和内容
        card_width = int(request.card_width) if request.card_width else 1200
        card_height = int(request.card_height) if request.card_height else 800
        scale = float(request.scale_value) if request.scale_value else 1.0
        # 使用 Markdown 解析器解析输入
        json_content = markdown_parser.parse_to_json(request.markdown_text)
        output_file_path="json_content.json"
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(json_content)
        generator = BlockGenerator({'width': card_width, 'height': card_height}, STYLE_CONFIG)
        layout_infos, blocks = generator.generate_blocks(json_content)
        #print("layout_infos:",layout_infos)
        # 使用模型生成布局
        final_positions = generate_layout(
            layout_model,
            card_width,
            card_height,
            blocks
        )
       
        #print("final_positions",final_positions)
        # 更新布局并生成 JSON
        #final_positions=[[891.75, 17.5, 826.5, 665.0],[21.75, 717.5, 826.5, 665.0],[21.75, 17.5, 826.5, 665.0],[891.75, 717.5, 848.25, 665.0]]
        
        layout_json = generator.update_layout_and_get_content(json_content, layout_infos, final_positions, card_width,scale)

        # 保存布局 JSON 到本地文件
        output_json_path = "layout_output.json"
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(layout_json, f, indent=4, ensure_ascii=False)
        card_size = {"width": card_width*scale, "height": card_height*scale}
        # 样式优化
        style_generator = StyleRuleGenerator(
            layout_info=layout_json,
            card_size=card_size,
            theme_color=request.theme_color
        )
        style_rules = style_generator.generate()

        # 运行时管理器生成 HTML
        runtime = RuntimeManager(
            layout_info=layout_json,
            card_size=card_size,
            style_rules=style_rules,
            scale=scale
        )
        html = runtime.generate_html(scale)

        # 保存 HTML 到本地文件

        output_file_path = "generated-local.html"
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html)

        print("HTML 文件已生成并保存至:", output_file_path)
        return LayoutResponse(layout_json=html)

    except Exception as e:
        print(f"生成布局时出错: {str(e)}")
        return None

if __name__ == "__main__":
    
    # 本地调用示
    markdown_input = """

# 节假日信息\\n根据中国国家假日办发布的节假日放假信息，您距离今天最近的节假日为圣诞节，预计放假天数为1天，祝您出行愉快！需要注意的是，假期安排可能会有调整，建议提前确认。\\n\\n# 请假方案\\n####请假理由：\\n个人健康与家庭事务\\n####请假开始时间：\\n2024-12-23 09:00\\n####请假结束时间：\\n2024-12-27 18:00\\n####请假时长：\\n5天\\n\\n# 请假日期\\n| 日期   | 星期 | 备注   |\\n| ------ | ---- | ------ |\\n| 12月23日 | 周一 | 请假   |\\n| 12月24日 | 周二 | 请假   |\\n| 12月25日 | 周三 | 请假   |\\n| 12月26日 | 周四 | 请假   |\\n| 12月27日 | 周五 | 请假   |\\n\\n# 请假日期\n根据您的假期时长，查询了近期适合出游的地点，建议前往以下地区及景点：\\n[chart:pie]| 日期     | 销量   |\n| -------- | ------ |\n| 2024-01-01 | 100    |\n| 2024-01-02 | 150    |\n根据您的假期时长，查询了近期适合出游的地点，建议前往以下地区及景点：\\n[chart:bar]| 日期     | 销量   |\n| -------- | ------ |\n| 2024-01-01 | 100    |\n| 2024-01-02 | 150    |\n\n
"""
    # 构建输入请求
    request = LayoutRequest(
        markdown_text=markdown_input,
        card_width="870",
        card_height="700",
        theme_color="",
        scale_value="1.0" )

    # 生成布局
    response = generate_layout_local(request)

    if response:
        print("生成的布局 HTML 内容：")
    else:
        print("布局生成失败。")
