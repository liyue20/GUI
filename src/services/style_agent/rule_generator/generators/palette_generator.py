import colorsys
from typing import Dict, List, Union

class PaletteGenerator:
    """调色板生成器：根据基础颜色生成卡片的三个渐变色方案"""
    
    def generate_palette(self, base_color: str) -> List[Dict]:
        """
        生成三个渐变色方案
        Args:
            base_color: 基础颜色，例如 '#3AE0A0'
        Returns:
            包含三个渐变方案的列表，从深到浅
        """
        try:
            h, s, l = self._hex_to_hsl(base_color)
            return [
                self._generate_dark_variant(h, s, l),    # 深色版本
                self._generate_medium_variant(h, s, l),  # 中等版本
                self._generate_light_variant(h, s, l)    # 浅色版本
            ]
        except Exception as e:
            print(f"Error generating palette for {base_color}: {str(e)}")
            return self._get_default_variants()
            
    def _generate_dark_variant(self, h: float, s: float, l: float) -> Dict:
        """生成深色版本"""
        return {
            'name': 'dark',
            'background': self._hsl_to_hex(h, s, l),  # 使用原始颜色
            'title': '#FFFFFF',  
            'icon': {
                'background': 'rgba(255,255,255,0.1)',
                'text': '#FFFFFF'
            },
            'content': '#FFFFFF',
            'time': '#FFFFFF',
            'button': {
                'background': '#FFFFFF',
                'text': '#FF6B6B'
            }
        }
        
    def _generate_medium_variant(self, h: float, s: float, l: float) -> Dict:
        """生成中等亮度版本"""
        return {
            'name': 'medium',
            'background': self._hsl_to_hex(h, s * 0.3, 0.95),  # 显著降低饱和度，提高亮度
            'title': '#333333',
            'icon': {
                'background': 'rgba(0,0,0,0.1)',
                'text': '#666666'
            },
            'content': '#666666',
            'time': '#666666',
            'button': {
                'background': '#FFFFFF',
                'text': '#FF6B6B'
            }
        }
        
    def _generate_light_variant(self, h: float, s: float, l: float) -> Dict:
        """生成浅色版本"""
        return {
            'name': 'light',
            'background': self._hsl_to_hex(h, s * 0.1, 0.98),  # 最低饱和度，最高亮度
            'title': '#333333',
            'icon': {
                'background': 'rgba(0,0,0,0.1)',
                'text': '#666666'
            },
            'content': '#666666',
            'time': '#666666',
            'button': {
                'background': '#FFFFFF',
                'text': '#FF6B6B'
            }
        }
        
    @staticmethod
    def _hex_to_hsl(hex_color: str) -> tuple:
        """将十六进制颜色转换为 HSL"""
        hex_color = hex_color.lstrip('#')
        rgb = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        h, l, s = colorsys.rgb_to_hls(*rgb)
        return h * 360, s, l
        
    @staticmethod
    def _hsl_to_hex(h: float, s: float, l: float) -> str:
        """将 HSL 转换为十六进制颜色"""
        r, g, b = colorsys.hls_to_rgb(h/360, l, s)
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'