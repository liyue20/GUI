from fastapi import APIRouter, HTTPException
from src.api.schemas.style import StylePaletteRequest, StylePaletteResponse, StyleScheme
from src.services.style_agent.rule_generator.generators.palette_generator import PaletteGenerator
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/palette", response_model=StylePaletteResponse)
async def generate_palette(request: StylePaletteRequest):
    """
    为多个主题色生成渐变色板
    
    Args:
        request: 包含主题色数组的请求体
        
    Returns:
        包含每个主题色的三个渐变方案的响应
    """
    try:
        # 初始化调色板生成器
        palette_generator = PaletteGenerator()
        
        # 存储所有主题色的结果
        all_palettes = {}
        
        # 处理每个主题色
        for base_color in request.theme_colors:
            # 获取当前主题色的三个渐变色板
            variants = palette_generator.generate_palette(base_color)
            
            # 转换为 StyleScheme 格式
            schemes = [
                StyleScheme(
                    background=variant['background'],
                    title=variant['title'],
                    icon=variant['icon'],
                    content=variant['content'],
                    time=variant['time'],
                    button=variant['button']
                )
                for variant in variants
            ]
            
            all_palettes[base_color] = schemes
        
        return StylePaletteResponse(palettes=all_palettes)
        
    except Exception as e:
        logger.error(f"Error generating color palettes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate color palettes: {str(e)}"
        )

@router.get("/health/check")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "style_agent"
    }