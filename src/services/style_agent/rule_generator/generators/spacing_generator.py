from .base_generator import BaseGenerator
from typing import Dict, Any

class SpacingGenerator(BaseGenerator):
    """间距生成器"""
    
    def __init__(self, config, typography_base_size: int = None):
        super().__init__(config)
        # 保存来自排版配置的基础字号，可用于联合计算
        self.typography_base_size = typography_base_size
    
    def _calculate_spacing(self, base_unit: int, scale: float) -> int:
        """计算具体间距值
        如果提供了 typography_base_size，则取 base_unit 和 typography_base_size 的平均值作为基数"""
        if self.typography_base_size is not None:
            effective_unit = (base_unit + self.typography_base_size) / 2
        else:
            effective_unit = base_unit
        return round(effective_unit * scale)
    
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