from .base_generator import BaseGenerator
from typing import Dict, Any

class TypographyGenerator(BaseGenerator):
    """排版生成器"""
    
    def _calculate_font_size(self, base_size: int, scale: float) -> int:
        """计算字体大小"""
        return round(base_size * scale)
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成排版规则"""
        base_size = self.config.TYPOGRAPHY_SYSTEM['base_size']
        
        # 生成字体大小比例尺
        font_sizes = {
            name: self._calculate_font_size(base_size, scale)
            for name, scale in self.config.TYPOGRAPHY_SYSTEM['scales'].items()
        }
        
        # 生成文本样式
        text_styles = {}
        for style_name, style_rules in self.config.TEXT_STYLES.items():
            text_styles[style_name] = {
                "font_size": font_sizes[style_rules['size']],
                "line_height": self.config.TYPOGRAPHY_SYSTEM['line_height'][style_rules['line_height']],
                "font_weight": self.config.TYPOGRAPHY_SYSTEM['weights'][style_rules['weight']]
            }
            
        return {
            "sizes": font_sizes,
            "styles": text_styles
        }