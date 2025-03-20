from .base_generator import BaseGenerator
import colorsys
import random
import math
from typing import Dict, Any, Tuple, List

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
    
    def _hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """将十六进制颜色转换为HSL"""
        r, g, b = [x/255.0 for x in self._hex_to_rgb(hex_color)]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        l = (max_val + min_val) / 2
        
        if max_val == min_val:
            h = s = 0  # 灰色
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
            
        return (h, s, l)
    
    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """将HSL转换为十六进制颜色"""
        def _hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        if s == 0:
            r = g = b = l  # 灰色
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = _hue_to_rgb(p, q, h + 1/3)
            g = _hue_to_rgb(p, q, h)
            b = _hue_to_rgb(p, q, h - 1/3)
            
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        return self._rgb_to_hex(rgb)
    
    def _adjust_color(self, color: str, saturation: float = None, 
                     lightness: float = None) -> str:
        """调整颜色的饱和度和亮度"""
        h, s, v = self._hex_to_hsv(color)
        
        if saturation is not None:
            s = max(0, min(1, saturation))
            
        if lightness is not None:
            v = max(0, min(1, lightness))
            
        return self._hsv_to_hex(h, s, v)
    
    def _generate_analogous_color(self, base_color: str, angle: float = 30) -> str:
        """生成类比色（相邻色相）"""
        h, s, v = self._hex_to_hsv(base_color)
        h_new = (h + angle/360) % 1.0
        return self._hsv_to_hex(h_new, s, v)
    
    def _generate_complementary_color(self, base_color: str) -> str:
        """生成互补色"""
        h, s, v = self._hex_to_hsv(base_color)
        h_new = (h + 0.5) % 1.0
        return self._hsv_to_hex(h_new, s, v)
    
    def _generate_triadic_colors(self, base_color: str) -> List[str]:
        """生成三元色"""
        h, s, v = self._hex_to_hsv(base_color)
        h1 = (h + 1/3) % 1.0
        h2 = (h + 2/3) % 1.0
        return [self._hsv_to_hex(h1, s, v), self._hsv_to_hex(h2, s, v)]
    
    def _generate_split_complementary_colors(self, base_color: str, angle: float = 30) -> List[str]:
        """生成分裂互补色"""
        h, s, v = self._hex_to_hsv(base_color)
        h_comp = (h + 0.5) % 1.0
        h1 = (h_comp + angle/360) % 1.0
        h2 = (h_comp - angle/360) % 1.0
        return [self._hsv_to_hex(h1, s, v), self._hsv_to_hex(h2, s, v)]
    
    def _generate_tetradic_colors(self, base_color: str) -> List[str]:
        """生成四元色"""
        h, s, v = self._hex_to_hsv(base_color)
        h1 = (h + 0.25) % 1.0
        h2 = (h + 0.5) % 1.0
        h3 = (h + 0.75) % 1.0
        return [
            self._hsv_to_hex(h1, s, v),
            self._hsv_to_hex(h2, s, v),
            self._hsv_to_hex(h3, s, v)
        ]
    
    def _generate_monochromatic_colors(self, base_color: str, count: int = 5) -> List[str]:
        """生成单色系列"""
        h, s, v = self._hex_to_hsv(base_color)
        colors = []
        
        for i in range(count):
            # 在保持色相不变的情况下，调整饱和度和亮度
            new_s = max(0, min(1, s - 0.1 + (i / (count-1)) * 0.2))
            new_v = max(0.3, min(0.9, v - 0.2 + (i / (count-1)) * 0.4))
            colors.append(self._hsv_to_hex(h, new_s, new_v))
            
        return colors
    
    def _generate_gradient(self, start_color: str, end_color: str, steps: int) -> List[str]:
        """生成两个颜色之间的渐变色"""
        start_rgb = self._hex_to_rgb(start_color)
        end_rgb = self._hex_to_rgb(end_color)
        
        r_step = (end_rgb[0] - start_rgb[0]) / (steps - 1)
        g_step = (end_rgb[1] - start_rgb[1]) / (steps - 1)
        b_step = (end_rgb[2] - start_rgb[2]) / (steps - 1)
        
        gradient = []
        for i in range(steps):
            r = int(start_rgb[0] + r_step * i)
            g = int(start_rgb[1] + g_step * i)
            b = int(start_rgb[2] + b_step * i)
            gradient.append(self._rgb_to_hex((r, g, b)))
            
        return gradient
    
    def _generate_vibrant_color(self, base_color: str) -> str:
        """生成更鲜艳的颜色变体"""
        h, s, v = self._hex_to_hsv(base_color)
        # 增加饱和度，保持适当亮度
        new_s = min(1.0, s * 1.3)
        new_v = min(0.95, v * 1.1)
        return self._hsv_to_hex(h, new_s, new_v)
    
    def _generate_muted_color(self, base_color: str) -> str:
        """生成更柔和的颜色变体"""
        h, s, v = self._hex_to_hsv(base_color)
        # 降低饱和度，调整亮度
        new_s = max(0.1, s * 0.7)
        new_v = min(0.9, v * 1.05)
        return self._hsv_to_hex(h, new_s, new_v)
    
    def _generate_color_scale(self, base_color: str) -> Dict[str, str]:
        """生成颜色比例尺"""
        h, s, v = self._hex_to_hsv(base_color)
        
        # 使用更丰富的颜色生成策略
        # 为浅色调增加一些微妙的色相变化
        light_hue_shift = random.uniform(-0.02, 0.02)
        # 为深色调增加不同的色相变化
        dark_hue_shift = random.uniform(-0.04, 0.04)
        
        # 为50-400的颜色使用更柔和的饱和度曲线
        light_saturation_curve = [0.1, 0.2, 0.3, 0.4, 0.5]
        # 为600-900的颜色使用更丰富的饱和度变化
        dark_saturation_curve = [0.65, 0.75, 0.85, 0.95]
        
        # 亮度曲线使用非线性变化
        light_value_curve = [0.97, 0.93, 0.89, 0.85, 0.80]
        dark_value_curve = [0.65, 0.55, 0.45, 0.35]
        
        return {
            "50": self._hsv_to_hex((h + light_hue_shift) % 1.0, light_saturation_curve[0], light_value_curve[0]),
            "100": self._hsv_to_hex((h + light_hue_shift * 0.8) % 1.0, light_saturation_curve[1], light_value_curve[1]),
            "200": self._hsv_to_hex((h + light_hue_shift * 0.6) % 1.0, light_saturation_curve[2], light_value_curve[2]),
            "300": self._hsv_to_hex((h + light_hue_shift * 0.3) % 1.0, light_saturation_curve[3], light_value_curve[3]),
            "400": self._hsv_to_hex((h + light_hue_shift * 0.1) % 1.0, light_saturation_curve[4], light_value_curve[4]),
            "500": base_color,
            "600": self._hsv_to_hex((h + dark_hue_shift * 0.2) % 1.0, dark_saturation_curve[0], dark_value_curve[0]),
            "700": self._hsv_to_hex((h + dark_hue_shift * 0.4) % 1.0, dark_saturation_curve[1], dark_value_curve[1]),
            "800": self._hsv_to_hex((h + dark_hue_shift * 0.7) % 1.0, dark_saturation_curve[2], dark_value_curve[2]),
            "900": self._hsv_to_hex((h + dark_hue_shift) % 1.0, dark_saturation_curve[3], dark_value_curve[3])
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
    
    def _generate_accent_color(self, base_color: str) -> str:
        """生成与主题色协调的强调色"""
        h, s, v = self._hex_to_hsv(base_color)
        h = (h + 0.05) % 1.0  # 调整色相，保持非常接近
        return self._hsv_to_hex(h, s, v)
    
    def _ensure_high_contrast(self, text_color: str, background_color: str, min_contrast: float = 4.5) -> str:
        """确保文本颜色与背景颜色之间的对比度足够高"""
        if self._calculate_contrast_ratio(text_color, background_color) >= min_contrast:
            return text_color
        
        # 调整文本颜色以提高对比度
        h, s, v = self._hex_to_hsv(text_color)
        bg_h, bg_s, bg_v = self._hex_to_hsv(background_color)
        
        if bg_v > 0.5:
            # 背景色偏亮，文本色需要变暗
            while v > 0 and self._calculate_contrast_ratio(self._hsv_to_hex(h, s, v), background_color) < min_contrast:
                v -= 0.05
        else:
            # 背景色偏暗，文本色需要变亮
            while v < 1 and self._calculate_contrast_ratio(self._hsv_to_hex(h, s, v), background_color) < min_contrast:
                v += 0.05
                
        return self._hsv_to_hex(h, s, v)
    
    def _generate_color_theme(self, base_color: str) -> Dict[str, Dict[str, str]]:
        """生成完整的颜色主题"""
        # 生成基础色阶
        primary_scale = self._generate_color_scale(base_color)
        
        # 生成强调色
        accent = self._generate_accent_color(base_color)
        accent_scale = self._generate_color_scale(accent)
        
        # 生成辅助色系
        h, s, v = self._hex_to_hsv(base_color)
        analogous1 = self._generate_analogous_color(base_color, 30)
        secondary_scale = self._generate_color_scale(analogous1)
        
        # 生成布局颜色 - 使用更丰富的颜色组合
        layout_colors = {
            "card": {
                "background": primary_scale["50"],  # 使用最浅的主色调
                "border": primary_scale["200"]      # 使用较浅的主色调作为边框
            },
            "block": {
                "background": self._adjust_color(secondary_scale["100"], saturation=0.15, lightness=0.95),
                "border": self._adjust_color(secondary_scale["300"], saturation=0.25, lightness=0.85)
            }
        }
        
        # 生成组件颜色 - 使用更多样的颜色组合
        component_colors = {
            "title_background": {
                "h1": self._adjust_color(primary_scale["400"], saturation=0.4, lightness=0.85),  # 鲜艳的标题背景
                "h2": self._adjust_color(primary_scale["300"], saturation=0.4, lightness=0.85),
                "h3": self._adjust_color(secondary_scale["200"], saturation=0.3, lightness=0.9),
                "h4": self._adjust_color(secondary_scale["100"], saturation=0.2, lightness=0.95),
                "h5": self._generate_muted_color(primary_scale["100"])     # 柔和的小标题背景
            },
            "subsection": {
                "background": self._adjust_color(accent_scale["100"], saturation=0.15, lightness=0.96),
                "border": self._adjust_color(accent_scale["300"], saturation=0.3, lightness=0.85)
            },
            "content": {
                "background": self._adjust_color(primary_scale["50"], saturation=0.05, lightness=0.98)
            }
        }
        
        # 生成文本颜色 - 确保良好的对比度
        typography_colors = {
            "title": {
                "h1": self._ensure_high_contrast(primary_scale["900"], component_colors["title_background"]["h1"]),
                "h2": self._ensure_high_contrast(primary_scale["900"], component_colors["title_background"]["h2"]),
                "h3": self._ensure_high_contrast(secondary_scale["900"], component_colors["title_background"]["h3"]),
                "h4": self._ensure_high_contrast(secondary_scale["900"], component_colors["title_background"]["h4"]),
                "h5": self._ensure_high_contrast(primary_scale["900"], component_colors["title_background"]["h5"])
            },
            "text": {
                "primary": "#000000",    # 固定为纯黑色
                "secondary": self._ensure_high_contrast(secondary_scale["900"], layout_colors["card"]["background"])
            }
        }
        
        # 添加一些额外的强调色和功能色
        accent_colors = {
            "info": accent_scale["500"],
            "success": self._hsv_to_hex(0.33, 0.8, 0.8),  # 绿色 
            "warning": self._hsv_to_hex(0.1, 0.9, 0.9),   # 橙色 
            "error": self._hsv_to_hex(0.0, 0.8, 0.8)      # 红色 
        }
        
        return {
            "primary": primary_scale,
            "secondary": secondary_scale,
            "accent": accent_scale,
            "typography": typography_colors
        }
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成颜色规则"""
        try:
            # 获取主题色
            base_color = self.config.theme_color
            
            # 生成完整的颜色主题
            color_theme = self._generate_color_theme(base_color)
            
            # 主色系
            primary_scale = color_theme["primary"]
            # 辅助色系
            secondary_scale = color_theme["secondary"]
            # 强调色系
            accent_scale = color_theme["accent"]
            
            # 生成布局颜色 - 使用更丰富的颜色组合
            layout_colors = {
                "card": {
                    "background": primary_scale["50"],  # 使用最浅的主色调
                    "border": primary_scale["200"]      # 使用较浅的主色调作为边框
                },
                "block": {
                    "background": self._adjust_color(secondary_scale["100"], saturation=0.15, lightness=0.95),
                    "border": self._adjust_color(secondary_scale["300"], saturation=0.25, lightness=0.85)
                }
            }
            
            # 生成组件颜色 - 使用更多样的颜色组合
            component_colors = {
                "title_background": {
                    "h1": self._generate_vibrant_color(primary_scale["400"]),  # 鲜艳的标题背景
                    "h2": self._adjust_color(primary_scale["300"], saturation=0.4, lightness=0.85),
                    "h3": self._adjust_color(secondary_scale["200"], saturation=0.3, lightness=0.9),
                    "h4": self._adjust_color(secondary_scale["100"], saturation=0.2, lightness=0.95),
                    "h5": self._generate_muted_color(primary_scale["100"])     # 柔和的小标题背景
                },
                "subsection": {
                    "background": self._adjust_color(accent_scale["100"], saturation=0.15, lightness=0.96),
                    "border": self._adjust_color(accent_scale["300"], saturation=0.3, lightness=0.85)
                },
                "content": {
                    "background": self._adjust_color(primary_scale["50"], saturation=0.05, lightness=0.98)
                }
            }
            
            # 生成文本颜色 - 确保良好的对比度
            typography_colors = {
                "title": {
                    "h1": self._ensure_high_contrast(primary_scale["900"], component_colors["title_background"]["h1"]),
                    "h2": self._ensure_high_contrast(primary_scale["800"], component_colors["title_background"]["h2"]),
                    "h3": self._ensure_high_contrast(secondary_scale["700"], component_colors["title_background"]["h3"]),
                    "h4": self._ensure_high_contrast(secondary_scale["600"], component_colors["title_background"]["h4"]),
                    "h5": self._ensure_high_contrast(primary_scale["500"], component_colors["title_background"]["h5"])
                },
                "text": {
                    "primary": "#000000",    # 固定为纯黑色
                    "secondary": self._ensure_high_contrast(secondary_scale["700"], layout_colors["card"]["background"])
                }
            }
            
            # 添加一些额外的强调色和功能色
            accent_colors = {
                "info": accent_scale["500"],
                "success": self._hsv_to_hex(0.33, 0.8, 0.8),  # 绿色 
                "warning": self._hsv_to_hex(0.1, 0.9, 0.9),   # 橙色 
                "error": self._hsv_to_hex(0.0, 0.8, 0.8)      # 红色 
            }
            
            return {
                "theme": {
                    "primary": primary_scale,
                    "secondary": secondary_scale,
                    "accent": accent_scale
                },
                "accent": accent_colors,
                "layout": layout_colors,
                "component": component_colors,
                "typography": typography_colors
            }
            
        except Exception as e:
            raise RuntimeError(f"生成颜色规则失败: {str(e)}")