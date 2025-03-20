from typing import Dict, Any
from .converter import LayoutParser, StyleApplier,LayoutParser_eight,HTMLContentAdjuster
import json
class RuntimeManager:
    """运行时管理器 - 协调布局解析和样式应用"""
    
    def __init__(self, layout_info: Dict[str, Any], card_size: Dict[str, int], style_rules: Dict[str, Any],scale):
        self.layout_info = layout_info
        self.card_size = card_size
        self.style_rules = style_rules
        self.scale=scale
        self.layout_parser = LayoutParser(layout_info, card_size)
        self.layout_parser_eight =LayoutParser_eight(layout_info,card_size)
        self.style_applier = StyleApplier(style_rules,scale)
        self.style_adjuster = HTMLContentAdjuster()
    
    def generate_html(self,scale) -> str:
        """生成完整的HTML"""
        try:
            # 1. 解析布局生成基础HTML
            base_html = self.layout_parser.parse()
            #base_json = self.layout_parser_eight.parse()
            #if isinstance(base_json, list) and len(base_json) == 1 and isinstance(base_json[0], dict):
            #    base_json = base_json[0]
            #with open('base_output.json','w',encoding='utf-8') as f:
            #   json.dump(base_json,f,ensure_ascii=False,indent=4)
            # 2. 应用样式规则
            #base_html_path = "/home/liyue/dingdaocode/aigui-model-service/test/generated-map.html"
            #with open(base_html_path, "r", encoding="utf-8") as f:
            #    base_html = f.read()
            complete_html = self.style_applier.apply(base_html,scale)
            adjusted_html = self.style_adjuster.process_html(complete_html,scale)
            return adjusted_html
            
        except Exception as e:
            raise RuntimeError(f"HTML生成失败: {str(e)}")
    
    
    def save_html(self, filepath: str,scale):
        """保存HTML到文件"""
        try:
            html = self.generate_html(scale)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            raise RuntimeError(f"HTML保存失败: {str(e)}")
    
    def generate_eight_element(self) -> str:
        """生成 8 要素 json"""
        try:
            base_json = self.layout_parser_eight.parse()
            if isinstance(base_json, list) and len(base_json) == 1 and isinstance(base_json[0], dict):
                base_json = base_json[0]

            if base_json is not None:
                input_value_str = json.dumps(base_json)  # 将 JSON 转换为字符串
                return input_value_str 
            return "" 
        except Exception as e:
            raise RuntimeError(f"8要素生成失败：{str(e)}")
        
    
    
        