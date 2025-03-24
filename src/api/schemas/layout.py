from enum import Enum
from typing import Optional
from pydantic import BaseModel, validator


class LayoutRequest(BaseModel):
    markdown_text: Optional[str] = "请传入文本"
    card_width: Optional[str] = "800"  
    card_height: Optional[str] = "800"  
    theme_color: Optional[str] = ""  
    scale_value: Optional[str] = "1.0"
    is_html: Optional[bool] = False

    @validator('card_width', 'card_height')
    def validate_dimensions(cls, v):
        if not v:  # 如果是空字符串
            return "800"  # 返回默认值 "800"
        try:
            return str(int(v))  # 转换为整数再转回字符串，确保是有效的整数字符串
        except ValueError:
            raise ValueError('尺寸必须是有效的整数字符串')
    
    @validator('markdown_text')
    def validate_markdown_text(cls, v):
        if not v or v.strip() == "":
            return "请传入文本"
        return v

class LayoutResponse(BaseModel):
    layout_json: str