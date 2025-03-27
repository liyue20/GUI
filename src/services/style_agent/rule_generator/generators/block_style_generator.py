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

    def load_css(self):
        css_styles = {
            "card": {
                "1": """  
                    margin: 0 auto;
                    background-color: var(--color-layout-card-background);
                    padding: 30px;
                    border-left: 5px solid var(--color-layout-card-border);
                    
                """,
                "2": """  
                    margin: 0 auto;
                    --input-focus: #2d8cf0;
                    --font-color: var(--color-typography-text-primary);
                    --font-color-sub: #666;
                    --bg-color: var(--color-layout-card-background);
                    --main-color: #323232;
                    padding: 20px;
                    background: var(--color-layout-card-background);
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    justify-content: center;
                    gap: 20px;
                    border-radius: 5px;
                    border: 2px solid var(--color-layout-card-border);
                    box-shadow: 4px 4px var(--color-layout-card-border);
                """,
                "3": """  
                    margin: 0 auto;
                    background-color: var(--color-layout-card-background);
                    display: block;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
                                0 4px 6px -2px rgba(0, 0, 0, 0.05);
                """,
                # "4": """
                #     margin: 0 auto;
                #     display: flex;
                #     flex-direction: column;
                #     align-items: center;
                #     background-color: var(--color-layout-card-background);
                #     width: 15.5em;
                #     height: 22.5em;
                #     border: 2px solid var(--color-layout-card-border);
                #     border-bottom-left-radius: 5em;
                #     border-top-right-radius: 5em;
                #     box-shadow: -10px 0px 0px #fffffa,
                #                 -10px 5px 5px rgba(255, 255, 255, 0.2);
                #     overflow: hidden;
                #     position: relative;
                #     transition: all 0.25s ease;
                # """,
                "4": """    
                    margin: 0 auto;
                    --main-col: #ffeba7;
                    --bg-col: #2a2b38;
                    --bg-field: #1f2029;
                    width: 190px;
                    padding: 1.9rem 1.2rem;
                    text-align: center;
                    background: var(--color-layout-card-background);
                    border-radius: 10px;
                    border: 5px solid var(--color-layout-card-border);
                    user-select: none;
                """,


                "5": """      
                        margin: 0 auto;  
                        border-radius: 5px;
                        border: 2px solid var(--color-layout-card-border);
                        background-color: var(--color-layout-card-background);)  ;
                        box-shadow: 4px 4px #000000;
                        font-size: 17px;
                        font-weight: 600;
                        color: var(--color-typography-text-primary);
                        cursor: pointer;
                        fill: var(--color-layout-card-background);
                    """,
                "6": """  
                        margin: 0 auto;  
                        background-color: var(--color-layout-card-background);
                        color: var(--color-typography-text-primary);
                        border: 0;
                        border-radius: 24px;
                        padding: 10px 16px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: var(--color-layout-card-background) .3s ease;
                    """,
                "7": """   
                        margin: 0 auto;  
                        position: absolute;
                        backface-visibility: hidden;
                        padding: 15px 20px;
                        border-radius: 15px;
                        box-shadow: inset 2px 2px 10px rgba(0,0,0,1),
                                    inset -1px -1px 5px rgba(255, 255, 255, 0.6);
                    """,
                "8": """  
                        margin: 0 auto;
                        overflow: auto;
                          --white: hsl(0, 0%, 100%);
                          --black: hsl(240, 15%, 9%);
                          --paragraph: hsl(0, 0%, 83%);
                          --line: hsl(240, 9%, 17%);
                          --primary: hsl(189, 92%, 58%);

                          position: relative;

                          display: flex;
                          flex-direction: column;
                          gap: 1rem;

                          padding: 1rem;
                          width: 19rem;
                          background-color: var(--color-layout-block-background);
                          background-image: radial-gradient(
                              at 88% 40%,
                              var(--color-theme-accent-800) 0px,
                              transparent 85%
                            ),
                            radial-gradient(at 49% 30%, var(--color-component-content-background) 0px, transparent 85%),
                            radial-gradient(at 14% 26%, var(--color-theme-accent-700) 0px, transparent 85%),
                            radial-gradient(at 0% 64%, var(--color-theme-accent-500) 0px, transparent 85%),
                            radial-gradient(at 41% 94%, var(--color-theme-accent-700) 0px, transparent 85%),
                            radial-gradient(at 100% 99%, var(--color-theme-accent-900) 0px, transparent 85%);


                          border-radius: 1rem;
                          box-shadow: 0px -16px 24px 0px rgba(255, 255, 255, 0.25) inset;""",
                "9": """ 
                            margin: 0 auto;
                            ustify-content: center;
                              background: linear-gradient(135deg, var(color-theme-accent-50), var(color-theme-accent-800));
                              color: white;
                              padding: 14px 28px;
                              border-radius: 50px;
                              cursor: pointer;
                              transition:
                                background 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
                                transform 0.3s ease,
                                box-shadow 0.4s ease;
                              box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
                              position: relative;
                              z-index: 10;
                              overflow: hidden;"""
            },
            "block": {
                "1": """  
                    overflow: auto;
                    position: relative;
                    text-align: left;
                    padding: 10px;
                    color: #caf438;
                    font-weight: bold;
                    background: var(--color-layout-block-background);
                    clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), 
                                       calc(100% - 10px) 100%, 0 100%);
                    transition: all 0.2s ease-in-out;
                """,
                "2": """   
                    overflow: auto;     
                 
                    border-radius: 5px;
                    border: 2px solid #000000;
                    background-color: var(--color-layout-block-background);
                    box-shadow: 4px 4px #000000;
                    font-size: 17px;
                    font-weight: 600;
                    color: var(--font-color);
                    cursor: pointer;
                    fill: var(--main-color);
                """,
                "3": """  
                     overflow: auto;
                    background-color: var(--color-layout-block-background);
                    color: var(color-layout-block-background);
                    border: 0;
                    border-radius: 24px;
                    padding: 10px 16px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color .3s ease;
                """,
                "4": """   
                    overflow: auto;
                    position: absolute;
                    backface-visibility: hidden;
                    padding: 15px 20px;
                    border-radius: 15px;
                    box-shadow: inset 2px 2px 10px rgba(0,0,0,1),
                                inset -1px -1px 5px rgba(255, 255, 255, 0.6);
                """,
                # "5": """
                #          overflow: auto;
                #         background-color: var(--color-layout-block-background);
                #         padding: 30px;
                #         border-left: 5px solid #ff7a01;
                #         clip-path: polygon(0 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%);
                #     """,
                "5": """  
                         overflow: auto;
                        --input-focus: #2d8cf0;
                        --font-color: #323232;
                        --font-color-sub: #666;
                        --bg-color: var(color-layout-block-background);
                        --main-color: #323232;

                        background: var(--color-layout-block-background);


                        justify-content: center;
                        gap: 10px;
                        border-radius: 5px;
                        border: 2px solid var(--color-layout-block-border);
                        box-shadow: 4px 4px var(--main-color);
                    """,
                "6": """  
                         overflow: auto;
                        background-color: var(--color-layout-block-background);
                        display: block;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
                                    0 4px 6px -2px rgba(0, 0, 0, 0.05);
                    """,
                # "7": """
                #          overflow: auto;
                #           display: flex;
                #         flex-direction: column;
                #
                #         background-color: var(--color-layout-block-background);
                #         width: 15.5em;
                #         height: 22.5em;
                #         border: 2px solid var(--color-layout-block-border);
                #         border-bottom-left-radius: 5em;
                #         border-top-right-radius: 5em;
                #         box-shadow: -10px 0px 0px var(--color-layout-card-border);,
                #                     -10px 5px 5px rgba(255, 255, 255, 0.2);
                #         overflow: hidden;
                #         position: relative;
                #         transition: all 0.25s ease;
                #     """,
                "7": """    
                         overflow: auto;
                        --main-col: #ffeba7;
                        --bg-col: #2a2b38;
                        --bg-field: #1f2029;
                        width: 190px;
                        padding: 1.9rem 1.2rem;
                        text-align: center;
                        background: var(--color-layout-block-background);
                        border-radius: 10px;
                        border: 5px solid var(--main-col);
                        user-select: none;
                    """,
                "8": """  
                          margin: 0 auto;
                        overflow: auto;
                          --white: hsl(0, 0%, 100%);
                          --black: hsl(240, 15%, 9%);
                          --paragraph: hsl(0, 0%, 83%);
                          --line: hsl(240, 9%, 17%);
                          --primary: hsl(189, 92%, 58%);

                          position: relative;

                          display: flex;
                          flex-direction: column;
                          gap: 1rem;

                          padding: 1rem;
                          width: 19rem;
                          background-color: var(--color-layout-block-background);
                          background-image: radial-gradient(
                              at 88% 40%,
                              var(--color-theme-accent-800) 0px,
                              transparent 85%
                            ),
                            radial-gradient(at 49% 30%, var(--color-component-content-background) 0px, transparent 85%),
                            radial-gradient(at 14% 26%, var(--color-theme-accent-700) 0px, transparent 85%),
                            radial-gradient(at 0% 64%, var(--color-theme-accent-500) 0px, transparent 85%),
                            radial-gradient(at 41% 94%, var(--color-theme-accent-700) 0px, transparent 85%),
                            radial-gradient(at 100% 99%, var(--color-theme-accent-900) 0px, transparent 85%);

                          border-radius: 1rem;
                          box-shadow: 0px -16px 24px 0px rgba(255, 255, 255, 0.25) inset;""",
                "9": """  
                                 overflow: auto;
                                  align-items: center;
                                  justify-content: center;
                                  background: linear-gradient(135deg,var(--color-layout-block-background), var(--color-theme-secondary-200));
                                  color: white;
                                  padding: 14px 28px;
                                  border-radius: 50px;
                                  cursor: pointer;
                                  transition:
                                    background 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
                                    transform 0.3s ease,
                                    box-shadow 0.4s ease;
                                  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
                                  position: relative;
                                  z-index: 10;
                                  overflow: hidden;"""
            },
            "content": {
                # "1": """
                #     width: 100%;
                #     padding: 10px;
                #     outline: none;
                #     border: none;
                #     color: #000;
                #     font-size: 1em;
                #     background: transparent;
                #     border-left: 2px solid #000;
                #     border-bottom: 2px solid #000;
                #     transition: 0.1s;
                #     border-bottom-left-radius: 8px;
                # """
                "1": """
           width: 100%;
                  border: solid 1px var(--color-typography-text-primary);
                  background-color: var(--color-component-content-background);

                  border-radius: 10px;
                  padding: 10px;
                  color: var(--color-typography-text-primary);
                  box-shadow: 0px 8px 20px -10px var(--color-typography-text-secondary);
                  text-shadow: 0px 0px 5px var(--color-theme-accent-50);
                  letter-spacing: 1px;
                  background-image: radial-gradient(circle 160px at 50% 120%, var(--color-theme-accent-50), var(--color-theme-accent-300));"""
             },
            "title-1": {
                "1": """   
                      margin-bottom: 1rem;
                    color: var(--color-typography-text-primary);
                    text-shadow: 1px 1px 20px var(--color-typography-text-secondary);
                    text-transform: uppercase;
                """,
                "2": """  
                    display: block;
                    margin-top: -0.5rem;
                    font-size: 2.1rem;
                    font-weight: 800;
                    font-family: Arial, Helvetica, sans-serif;
                    text-align: center;
                    -webkit-text-stroke: #fff 0.1rem;
                    letter-spacing: 0.2rem;
                    color: transparent;
                    position: relative;
                    text-shadow: 0px 0px 16px #CECECE;
                """
            }
        }

        return css_styles






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