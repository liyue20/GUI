from .base_generator import BaseGenerator
import random
from typing import Dict, Any

class BlockStyleGenerator(BaseGenerator):
    """块样式生成器 - 生成块级元素的样式特性"""
    
    def __init__(self, config=None):
        """初始化块样式生成器"""
        super().__init__(config)
    
    def weighted_random_choice(self, options, weights):
        """根据权重随机选择选项"""
        return random.choices(options, weights=weights, k=1)[0]
    
    def random_in_range(self, min_val, max_val, weight):
        """在范围内随机生成值并应用权重"""
        return round(random.uniform(min_val, max_val) * weight)
    
    def generate_block_style(self):
        """生成块样式特性"""
        return {
            # 定义形状相关的特征
            "shape": {
                # 边框半径在 0 到 50 之间随机选择，步长为 0.8,
                "border_radius": self.random_in_range(0, 50, 0.8),
                # 是否有折叠效果，30% 的概率为 True，70% 的概率为 False
                "has_fold": self.weighted_random_choice([True, False], [0.3, 0.7]),
                # 是否有特殊角，40% 的概率为 True，60% 的概率为 False
                "has_special_corners": self.weighted_random_choice([True, False], [0.4, 0.6]),
                # 是否有边框，50% 的概率为 True，50% 的概率为 False
                "has_border": self.weighted_random_choice([True, False], [0.5, 0.5]),
                # 边框样式在 'solid', 'dashed', 'dotted', 'double' 中随机选择，权重分别为 0.4, 0.2, 0.2, 0.2
                "border_style": self.weighted_random_choice(['solid', 'dashed', 'dotted', 'double'], [0.4, 0.2, 0.2, 0.2]),
                # 边框宽度在 1 到 5 之间随机选择，步长为 0.6
                "border_width": self.random_in_range(1, 5, 0.6),
                # 是否不对称，30% 的概率为 True，70% 的概率为 False
                "is_asymmetric": self.weighted_random_choice([True, False], [0.3, 0.7]),
            },
            # 定义颜色相关的特征
            "color": {
                # 主要颜色使用 CSS 变量定义
                "primary_color": "var(--color-layout-block-background)",
                # 是否使用渐变，70% 的概率为 True，30% 的概率为 False
                "use_gradient": self.weighted_random_choice([True, False], [0.7, 0.3]),
                # 渐变类型在 'linear', 'radial', 'conic' 中随机选择，权重分别为 0.5, 0.3, 0.2
                "gradient_type": self.weighted_random_choice(['linear', 'radial', 'conic'], [0.5, 0.3, 0.2]),
                # 渐变方向在 'to right', 'to bottom', 'to bottom right', '135deg' 中随机选择，权重分别为 0.3, 0.3, 0.2, 0.2
                "gradient_direction": self.weighted_random_choice(['to right', 'to bottom', 'to bottom right', '135deg'],
                                                         [0.3, 0.3, 0.2, 0.2]),
                # 对比度级别在 3 到 10 之间随机选择，步长为 0.6
                "contrast_level": self.random_in_range(3, 10, 0.6),
                # 是否有边框颜色，60% 的概率为 True，40% 的概率为 False
                "has_border_color": self.weighted_random_choice([True, False], [0.6, 0.4]),
                # 是否有文本阴影，40% 的概率为 True，60% 的概率为 False
                "has_text_shadow": self.weighted_random_choice([True, False], [0.4, 0.6]),
                # 是否有模糊效果，30% 的概率为 True，70% 的概率为 False
                "has_blur_effect": self.weighted_random_choice([True, False], [0.3, 0.7]),
                # 模糊半径在 5 到 20 之间随机选择，步长为 0.5
                "blur_radius": self.random_in_range(5, 20, 0.5),
                # 背景滤镜效果在 'blur', 'brightness', 'contrast', 'grayscale', 'hue-rotate', 'opacity', 'saturate', 'sepia' 中随机选择
                "backdrop_filter": self.weighted_random_choice(
                    ['blur', 'brightness', 'contrast', 'grayscale', 'hue-rotate', 'opacity', 'saturate', 'sepia'],
                    [0.8, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]),
            },
            # 定义材料相关的特征
            "material": {
                # 光泽度在 0 到 10 之间随机选择，步长为 0.7
                "glossiness": self.random_in_range(5, 10, 0.7),
                # 透明度固定为 1
                "transparency": random.uniform(1, 1) * 1,
                # 是否有阴影，80% 的概率为 True，20% 的概率为 False
                "has_shadow": self.weighted_random_choice([True, False], [0.8, 0.2]),
                # 阴影强度在 1 到 20 之间随机选择，步长为 0.6
                "shadow_intensity": self.random_in_range(1, 20, 0.6),
                # 是否有内阴影，50% 的概率为 True，50% 的概率为 False
                "has_inset_shadow": self.weighted_random_choice([True, False], [0.5, 0.5]),
                # 是否有动态光照效果，40% 的概率为 True，60% 的概率为 False
                "has_dynamic_lighting": self.weighted_random_choice([True, False], [0.4, 0.6]),
                # 是否为新拟态风格，30% 的概率为 True，70% 的概率为 False
                "is_neumorphic": self.weighted_random_choice([True, False], [0.3, 0.7]),
            },
            # 定义布局相关的特征
            "layout": {
                # 水平填充在 10 到 60 之间随机选择，步长为 0.5
                "padding_x": self.random_in_range(10, 60, 0.5),
                # 垂直填充在 8 到 40 之间随机选择，步长为 0.5
                "padding_y": self.random_in_range(8, 40, 0.5),
                # 是否有图标，40% 的概率为 True，60% 的概率为 False
                "has_icon": self.weighted_random_choice([True, False], [0.4, 0.6]),
                # 图标位置在 'left', 'right' 中随机选择，权重分别为 0.7, 0.3
                "icon_position": self.weighted_random_choice(['left', 'right'], [0.7, 0.3]),
                # 图标是否有动画效果，50% 的概率为 True，50% 的概率为 False
                "has_icon_animation": self.weighted_random_choice([True, False], [0.5, 0.5]),
            },
            # 定义动画相关的特征
            "animation": {
                # 是否有悬停效果，90% 的概率为 True，10% 的概率为 False
                "has_hover_effect": self.weighted_random_choice([True, False], [0.9, 0.1]),
                # 动画持续时间在 0.2 到 2 之间随机选择，步长为 0.5
                "animation_duration": random.uniform(0.2, 2) * 0.5,
                # 动画类型在 'ease', 'ease-in', 'ease-out', 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' 中随机选择
                "animation_type": self.weighted_random_choice(
                    ['ease', 'ease-in', 'ease-out', 'cubic-bezier(0.175, 0.885, 0.32, 1.275)'], 
                    [0.4, 0.2, 0.2, 0.2]),
            }
        }
    
    def generate_block_css(self, features):
        """根据特性生成块的CSS样式"""
        # 背景处理（支持渐变）
        if features['color']['use_gradient']:
            background = f"{features['color']['gradient_type']}-gradient({features['color']['gradient_direction']}, var(--color-start), var(--color-end))"
        else:
            background = features['color']['primary_color']

        # 边框颜色处理
        border_color = "var(--color-border)" if features['color']['has_border_color'] else "transparent"

        # 阴影处理
        shadow_type = "inset " if features['material']['has_inset_shadow'] else ""
        shadow = f"{shadow_type}0px 0px {features['material']['shadow_intensity']}px rgba(0,0,0,0.3)" if \
            features['material']['has_shadow'] else "none"

        # 新拟态效果
        neumorphic_shadow = (
            "5px 5px 10px rgba(0, 0, 0, 0.2), -5px -5px 10px rgba(255, 255, 255, 0.7)"
            if features['material']['is_neumorphic'] else shadow
        )

        # 动态光效
        dynamic_light = "filter: brightness(1.1);" if features['material']['has_dynamic_lighting'] else ""

        # hover 动效
        hover_effect = "transform: scale(1.05);" if features['animation']['has_hover_effect'] else ""

        return {
            "border-radius": f"{features['shape']['border_radius']}px",
            "border-width": f"{features['shape']['border_width']}px",
            "border-style": features['shape']['border_style'],
            "border-color": border_color,
            "background": background,
            "padding": f"{features['layout']['padding_y']}px {features['layout']['padding_x']}px",
            "box-shadow": neumorphic_shadow,
            "opacity": features['material']['transparency'],
            "transition": f"all {features['animation']['animation_duration']}s {features['animation']['animation_type']}",
            "dynamic_light": dynamic_light,
            "hover_effect": hover_effect
        }
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成块样式规则"""
        try:
            # 生成块样式特性
            block_style_features = self.generate_block_style()
            
            # 根据特性生成CSS
            block_css = self.generate_block_css(block_style_features)
            
            return {
                "features": block_style_features,
                "css": block_css
            }
            
        except Exception as e:
            raise RuntimeError(f"生成块样式规则失败: {str(e)}") 