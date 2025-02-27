from pydantic import BaseModel, validator
from typing import List, Dict, Optional

class StyleElement:
    """样式元素"""
    color: str
    bgColor: str

class StyleScheme(BaseModel):
    """单个样式方案"""
    background: str
    title: str
    icon: Dict[str, str]  # {background: "", text: ""}
    content: str
    time: str
    button: Dict[str, str]  # {background: "", text: ""}

class StylePaletteRequest(BaseModel):
    """请求体"""
    theme_colors : List[str]

    @validator('theme_colors')
    def validate_hex_colors(cls, colors):
        for color in colors:
            if not color.startswith('#') or len(color) != 7:
                raise ValueError(f"Invalid hex color format: {color}. Must be in format '#RRGGBB'")
        return colors

class StylePaletteResponse(BaseModel):
    """响应体"""
    palettes: Dict[str, List[StyleScheme]]