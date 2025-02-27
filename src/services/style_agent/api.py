from typing import Dict, Any, Optional
from .rule_generator import StyleRuleGenerator

def generate_style(
    layout_info: Dict[str, Any] = None,
    card_size: Dict[str, int] = None,
    preset_name: Optional[str] = None,
    theme_color: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成样式API
    
    Args:
        layout_info: 布局信息，可选
        card_size: 卡片尺寸，可选
        preset_name: 预设名称，可选
        theme_color: 主题色，可选
    
    Returns:
        Dict[str, Any]: 包含样式规则和CSS的字典
    """
    try:
        # 设置默认值
        if layout_info is None:
            layout_info = {
                'density': 'comfortable',
                'text_density': 'comfortable'
            }
        
        if card_size is None:
            card_size = {'width': 1200, 'height': 800}
        
        # 创建生成器
        if preset_name:
            generator = StyleRuleGenerator.from_preset(
                layout_info=layout_info,
                card_size=card_size,
                preset_name=preset_name
            )
        else:
            generator = StyleRuleGenerator(
                layout_info=layout_info,
                card_size=card_size,
                theme_color=theme_color
            )
        
        # 生成样式
        style_rules = generator.generate()
        css = generator.generate_css()
        
        return {
            "success": True,
            "data": {
                "rules": style_rules,
                "css": css
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 