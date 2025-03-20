from enum import Enum
from typing import Optional
from pydantic import BaseModel, validator


class LayoutRequest(BaseModel):
    markdown_text: str
    card_width: str  # Changed to str
    card_height: str  # Changed to str
    theme_color: str
    scale_value: Optional[str] = "1.0"
    is_html: Optional[bool] = False

    @validator('card_width', 'card_height')
    def validate_dimensions(cls, v):
        if not v:  # If empty string
            return v  # Keep as empty string for later handling
        try:
            return int(v)  # Convert to integer if possible
        except ValueError:
            raise ValueError('Dimensions must be valid integer strings or empty')

class LayoutResponse(BaseModel):
    layout_json: str