from typing import Dict, Any, Optional
from dataclasses import dataclass
import random

@dataclass
class StylePreset:
    """样式预设"""
    name: str
    color_preset: str
    typography_preset: str
    spacing_preset: str
    description: str

class StylePresetManager:
    """样式预设管理器"""
    
    # 预定义的样式组合
    STYLE_PRESETS = [
        StylePreset(
            name="modern_compact",
            color_preset="blue",
            typography_preset="compact",
            spacing_preset="compact",
            description="现代简约风格，紧凑布局"
        ),
        StylePreset(
            name="classic_comfortable",
            color_preset="green",
            typography_preset="comfortable",
            spacing_preset="balanced",
            description="经典舒适风格，平衡布局"
        ),
        StylePreset(
            name="elegant_spacious",
            color_preset="purple",
            typography_preset="spacious",
            spacing_preset="spacious",
            description="优雅宽敞风格，舒适布局"
        ),
        StylePreset(
            name="bold_contrast",
            color_preset="orange",
            typography_preset="comfortable",
            spacing_preset="compact",
            description="大胆对比风格，紧凑布局"
        ),
        StylePreset(
            name="minimal_clean",
            color_preset="teal",
            typography_preset="compact",
            spacing_preset="balanced",
            description="极简清爽风格，平衡布局"
        )
    ]
    
    @classmethod
    def get_preset(cls, name: str) -> Optional[StylePreset]:
        """获取指定名称的预设"""
        return next((p for p in cls.STYLE_PRESETS if p.name == name), None)
    
    @classmethod
    def get_random_preset(cls) -> StylePreset:
        """获取随机预设"""
        return random.choice(cls.STYLE_PRESETS)
    
    @classmethod
    def create_custom_preset(cls, 
                           name: str,
                           color_preset: str,
                           typography_preset: str,
                           spacing_preset: str,
                           description: str = "") -> StylePreset:
        """创建自定义预设"""
        return StylePreset(
            name=name,
            color_preset=color_preset,
            typography_preset=typography_preset,
            spacing_preset=spacing_preset,
            description=description
        ) 