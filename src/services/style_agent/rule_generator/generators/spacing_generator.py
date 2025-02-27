from .base_generator import BaseGenerator
from typing import Dict, Any

class SpacingGenerator(BaseGenerator):
    """间距生成器"""
    
    def _calculate_spacing(self, base_unit: int, scale: float) -> int:
        """计算具体间距值"""
        return round(base_unit * scale)
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成间距规则"""
        base_unit = self.config.SPACING_SYSTEM['base_unit']
        
        # 生成基础间距比例尺
        spacing_scale = {
            name: self._calculate_spacing(base_unit, scale)
            for name, scale in self.config.SPACING_SYSTEM['scales'].items()
        }
        
        # 生成布局间距规则
        layout_spacing = {}
        for component, rules in self.config.LAYOUT_SPACING.items():
            layout_spacing[component] = {
                key: spacing_scale[value] if isinstance(value, str) else value
                for key, value in rules.items()
            }
        
        return {
            "scale": spacing_scale,
            "layout": layout_spacing
        }