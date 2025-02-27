from typing import Dict, List, Any
import colorsys

class ActionSpace:
    """动作空间定义"""
    
    def __init__(self):
        # 定义可用的动作
        self.actions = [
            'increase_contrast',
            'decrease_contrast',
            'increase_brightness',
            'decrease_brightness',
            'increase_saturation',
            'decrease_saturation',
            'shift_hue_positive',
            'shift_hue_negative'
        ]
        
        # 动作参数
        self.step_sizes = {
            'contrast': 0.1,
            'brightness': 0.1,
            'saturation': 0.1,
            'hue': 0.05
        }
    
    def get_action_size(self) -> int:
        """获取动作空间大小"""
        return len(self.actions)
    
    def get_action(self, action_idx: int) -> str:
        """获取动作名称"""
        return self.actions[action_idx]
    
    def apply_action(self, action: str, style: Dict) -> Dict:
        """应用动作到样式上"""
        new_style = self._deep_copy_style(style)
        
        if action.startswith('increase') or action.startswith('decrease'):
            # 获取调整方向
            increase = action.startswith('increase')
            # 获取调整类型
            adjust_type = action.split('_')[1]
            # 应用调整
            new_style = self._adjust_colors(new_style, adjust_type, increase)
            
        elif action.startswith('shift_hue'):
            # 获取调整方向
            positive = action.endswith('positive')
            # 应用色相调整
            new_style = self._adjust_hue(new_style, positive)
        
        return new_style
    
    def _deep_copy_style(self, style: Dict) -> Dict:
        """深拷贝样式对象"""
        return {
            'colors': style['colors'].copy(),
            'typography': style['typography'].copy(),
            'spacing': style['spacing'].copy()
        }
    
    def _adjust_colors(self, style: Dict, adjust_type: str, increase: bool) -> Dict:
        """调整颜色属性"""
        step = self.step_sizes[adjust_type]
        if not increase:
            step = -step
            
        for color_key in style['colors']:
            hex_color = style['colors'][color_key]
            # 转换为HSL
            h, s, l = self._hex_to_hsl(hex_color)
            
            if adjust_type == 'contrast':
                # 对比度调整通过改变与中性灰的距离
                l = l + step if l > 0.5 else l - step
            elif adjust_type == 'brightness':
                l = l + step
            elif adjust_type == 'saturation':
                s = s + step
            
            # 确保值在有效范围内
            s = max(0, min(1, s))
            l = max(0, min(1, l))
            
            # 转换回hex
            style['colors'][color_key] = self._hsl_to_hex(h, s, l)
            
        return style
    
    def _adjust_hue(self, style: Dict, positive: bool) -> Dict:
        """调整色相"""
        step = self.step_sizes['hue']
        if not positive:
            step = -step
            
        for color_key in style['colors']:
            hex_color = style['colors'][color_key]
            h, s, l = self._hex_to_hsl(hex_color)
            
            # 调整色相
            h = (h + step) % 1
            
            style['colors'][color_key] = self._hsl_to_hex(h, s, l)
            
        return style
    
    def _hex_to_hsl(self, hex_color: str) -> tuple:
        """将十六进制颜色转换为HSL"""
        # 移除'#'号并转换为RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:], 16) / 255.0
        
        # 转换为HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return h, s, l
    
    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """将HSL转换为十六进制颜色"""
        # 转换为RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        
        # 转换为hex
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'