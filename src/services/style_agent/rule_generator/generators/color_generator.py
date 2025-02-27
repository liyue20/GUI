from .base_generator import BaseGenerator
import colorsys
from typing import Dict, Any, Tuple

class ColorGenerator(BaseGenerator):
    """颜色生成器"""
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """将RGB转换为十六进制颜色"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """将十六进制颜色转换为HSV"""
        rgb = self._hex_to_rgb(hex_color)
        return colorsys.rgb_to_hsv(*[x/255.0 for x in rgb])
    
    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """将HSV转换为十六进制颜色"""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb_int = tuple(int(x * 255) for x in rgb)
        return self._rgb_to_hex(rgb_int)
    
    def _adjust_color(self, color: str, saturation: float = None, 
                     lightness: float = None) -> str:
        """调整颜色的饱和度和亮度"""
        h, s, v = self._hex_to_hsv(color)
        
        if saturation is not None:
            s = max(0, min(1, saturation))
            
        if lightness is not None:
            v = max(0, min(1, lightness))
            
        return self._hsv_to_hex(h, s, v)
    
    def _generate_color_scale(self, base_color: str) -> Dict[str, str]:
        """生成颜色比例尺"""
        h, s, v = self._hex_to_hsv(base_color)
        
        return {
            "50": self._adjust_color(base_color, saturation=0.1, lightness=0.97),
            "100": self._adjust_color(base_color, saturation=0.2, lightness=0.95),
            "200": self._adjust_color(base_color, saturation=0.3, lightness=0.90),
            "300": self._adjust_color(base_color, saturation=0.4, lightness=0.85),
            "400": self._adjust_color(base_color, saturation=0.5, lightness=0.80),
            "500": base_color,
            "600": self._adjust_color(base_color, saturation=0.7, lightness=0.60),
            "700": self._adjust_color(base_color, saturation=0.8, lightness=0.50),
            "800": self._adjust_color(base_color, saturation=0.9, lightness=0.40),
            "900": self._adjust_color(base_color, saturation=1.0, lightness=0.30)
        }
    
    def _calculate_relative_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """计算相对亮度 (WCAG标准)"""
        rgb_normalized = [x/255 for x in rgb]
        rgb_adjusted = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055)**2.4 for x in rgb_normalized]
        return 0.2126 * rgb_adjusted[0] + 0.7152 * rgb_adjusted[1] + 0.0722 * rgb_adjusted[2]
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """计算两个颜色之间的对比度 (WCAG标准)"""
        lum1 = self._calculate_relative_luminance(self._hex_to_rgb(color1))
        lum2 = self._calculate_relative_luminance(self._hex_to_rgb(color2))
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)
    
    def _ensure_contrast(self, color: str, background: str, target_ratio: float) -> str:
        """确保颜色满足对比度要求"""
        if self._calculate_contrast_ratio(color, background) >= target_ratio:
            return color
            
        h, s, v = self._hex_to_hsv(color)
        bg_h, bg_s, bg_v = self._hex_to_hsv(background)
        
        # 根据背景色亮度决定调整方向
        if bg_v > 0.5:
            # 背景色偏亮，文本色需要变暗
            while v > 0 and self._calculate_contrast_ratio(self._hsv_to_hex(h, s, v), background) < target_ratio:
                v -= 0.05
        else:
            # 背景色偏暗，文本色需要变亮
            while v < 1 and self._calculate_contrast_ratio(self._hsv_to_hex(h, s, v), background) < target_ratio:
                v += 0.05
                
        return self._hsv_to_hex(h, s, v)
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成颜色规则"""
        try:
            # 获取主题色
            base_color = self.config.theme_color
            # 生成基础色阶
            color_scale = self._generate_color_scale(base_color)
            
            # 生成布局颜色
            layout_colors = {
                "card": {
                    "background": self._adjust_color(base_color, saturation=0.1, lightness=0.97),
                    "border": self._adjust_color(base_color, saturation=0.2, lightness=0.90)
                },
                "block": {
                    "background": self._adjust_color(base_color, saturation=0.15, lightness=0.93),
                    "border": self._adjust_color(base_color, saturation=0.25, lightness=0.85)
                }
            }
            
            # 生成组件颜色
            component_colors = {
                "title_background": {
                    "h1": self._adjust_color(base_color, saturation=0.4, lightness=0.75),
                    "h2": self._adjust_color(base_color, saturation=0.3, lightness=0.80),
                    "h3": self._adjust_color(base_color, saturation=0.2, lightness=0.85),
                    "h4": self._adjust_color(base_color, saturation=0.1, lightness=0.90),
                    "h5": self._adjust_color(base_color, saturation=0.05, lightness=0.95)
                },
                "subsection": {
                    "background": self._adjust_color(base_color, saturation=0.1, lightness=0.96),
                    "border": self._adjust_color(base_color, saturation=0.2, lightness=0.88)
                },
                "content": {
                    "background": self._adjust_color(base_color, saturation=0.05, lightness=0.98)
                }
            }
            
            # 生成文本颜色
            typography_colors = {
                "title": {
                    "h1": self._adjust_color(base_color, saturation=0.8, lightness=0.15),
                    "h2": self._adjust_color(base_color, saturation=0.7, lightness=0.20),
                    "h3": self._adjust_color(base_color, saturation=0.6, lightness=0.25),
                    "h4": self._adjust_color(base_color, saturation=0.5, lightness=0.30),
                    "h5": self._adjust_color(base_color, saturation=0.4, lightness=0.35)
                },
                "text": {
                    "primary": self._adjust_color(base_color, saturation=0.7, lightness=0.20),
                    "secondary": self._adjust_color(base_color, saturation=0.5, lightness=0.30)
                }
            }
            
            return {
                "theme": {
                    "primary": color_scale
                },
                "layout": layout_colors,
                "component": component_colors,
                "typography": typography_colors
            }
            
        except Exception as e:
            raise RuntimeError(f"生成颜色规则失败: {str(e)}")