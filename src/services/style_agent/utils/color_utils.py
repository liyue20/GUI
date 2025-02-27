# src/services/style_agent/utils/color_utils.py
import colorsys
from typing import Tuple

class ColorUtils:
    """颜色工具类"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        将十六进制颜色转换为RGB
        
        Args:
            hex_color: 十六进制颜色值 (例如 '#FF0000')
            
        Returns:
            Tuple[int, int, int]: RGB值
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """
        将RGB转换为十六进制颜色
        
        Args:
            rgb: RGB颜色值
            
        Returns:
            str: 十六进制颜色值
        """
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
        """
        将十六进制颜色转换为HSL
        
        Args:
            hex_color: 十六进制颜色值
            
        Returns:
            Tuple[float, float, float]: HSL值 (0-360, 0-1, 0-1)
        """
        # 转换为RGB
        rgb = ColorUtils.hex_to_rgb(hex_color)
        # 转换为0-1范围
        r, g, b = [x/255.0 for x in rgb]
        # 转换为HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        # 调整色相范围到0-360
        return (h * 360, s, l)
    
    @staticmethod
    def hsl_to_hex(h: float, s: float, l: float) -> str:
        """
        将HSL转换为十六进制颜色
        
        Args:
            h: 色相 (0-360)
            s: 饱和度 (0-1)
            l: 亮度 (0-1)
            
        Returns:
            str: 十六进制颜色值
        """
        # 调整色相范围到0-1
        h = h / 360
        # 转换为RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        # 转换为0-255范围
        rgb = tuple(int(x * 255) for x in (r, g, b))
        # 转换为十六进制
        return ColorUtils.rgb_to_hex(rgb)
    
    @staticmethod
    def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
        """
        计算相对亮度
        
        Args:
            rgb: RGB颜色值
            
        Returns:
            float: 相对亮度值
        """
        # 转换为0-1范围
        r, g, b = [x/255.0 for x in rgb]
        # sRGB转换
        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
        # 计算亮度
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def calculate_contrast(color1: str, color2: str) -> float:
        """
        计算两个颜色的对比度
        
        Args:
            color1: 第一个颜色（十六进制）
            color2: 第二个颜色（十六进制）
            
        Returns:
            float: 对比度值
        """
        # 计算两个颜色的亮度
        l1 = ColorUtils.calculate_luminance(ColorUtils.hex_to_rgb(color1))
        l2 = ColorUtils.calculate_luminance(ColorUtils.hex_to_rgb(color2))
        # 计算对比度
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

