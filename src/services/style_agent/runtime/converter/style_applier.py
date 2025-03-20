# runtime/converter/style_applier.py
import json
import uuid
from typing import Dict, Any
import random

class StyleApplier:
    """样式应用器"""
    
    def __init__(self, style_rules: Dict[str, Any], scale):
        self.style_rules = style_rules
        self.scale = scale
        self.unique_class = f"style-scope-{random.randint(1000, 9999)}"  # 添加唯一标识符

    def apply(self, html: str, scale) -> str:
        """应用样式生成完整HTML"""
        try:

            
            template = f"""
<!DOCTYPE html>
<html lang="zh-CN" class="{self.unique_class}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* CSS 变量 */
        {self._generate_css_variables(scale)}
        
        /* CSS 规则 */
        {self._generate_css_rules()}
    </style>
</head>
<body >
    <div class="{self.unique_class}">
        {html}
    </div>
</body>
</html>
"""
            return template
            
        except Exception as e:
            raise RuntimeError(f"应用样式失败: {str(e)}")
    
    def _generate_css_variables(self, scale) -> str:
        """生成CSS变量声明"""
        css_vars = [f".{self.unique_class}{{"]
        
        # 添加颜色变量
        for category, values in self.style_rules["color"].items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, dict):
                        for sub_key, color in value.items():
                            css_vars.append(f"    --color-{category}-{key}-{sub_key}: {color};")
                    else:
                        css_vars.append(f"    --color-{category}-{key}: {value};")
        
        # 添加强调色变量
        if "accent" in self.style_rules["color"]:
            for key, value in self.style_rules["color"]["accent"].items():
                css_vars.append(f"    --color-accent-{key}: {value};")
        
        # 添加间距变量
        spacing = self.style_rules.get("spacing", {})
        for key, value in spacing.get("scale", {}).items():
            css_vars.append(f"    --spacing-{key}: {value*scale*0.8}px;")
        
        # 添加排版变量
        typography = self.style_rules.get("typography", {})
        for key, value in typography.get("sizes", {}).items():
            css_vars.append(f"    --font-size-{key}: {value*scale}px;")
            
        # 添加动效变量
        if "animation" in self.style_rules:
            animation = self.style_rules["animation"]
            
            # 添加时间变量
            for name, value in animation.get("timing", {}).items():
                css_vars.append(f"    --animation-duration-{name}: {value};")
            
            # 添加缓动函数变量
            for name, value in animation.get("easing", {}).items():
                css_vars.append(f"    --animation-easing-{name}: {value};")
        
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def _generate_css_rules(self) -> str:
        """生成CSS规则"""
        animations = self.style_rules.get("animation", {}).get("animations", {})
        
        # 生成@keyframes规则
        keyframes_rules = []
        for category, anim in animations.items():
            keyframes_rules.append(f"""
@keyframes {anim['name']} {{
    {anim['keyframes']}
}}
""")
        
        # 随机选择一个悬停动画
        hover_animation = animations.get('hover', {}).get('name', 'none')
        
        # 将动画应用到相应的元素
        animation_css = f"""
/* 入场动画 */
.{self.unique_class} .block {{
    animation: var(--animation-duration-normal) var(--animation-easing-standard) both;
    animation-name: {animations.get('entrance', {}).get('name', 'none')};
    animation-delay: calc(var(--animation-duration-fast) * var(--animation-order, 0));
    background: linear-gradient(135deg, var(--color-theme-primary-100), var(--color-theme-primary-300));
    opacity: 0.95;
    transform-origin: center center;
    perspective: 1000px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* 悬停动画 */
.{self.unique_class} .block:hover {{
    animation: {hover_animation} var(--animation-duration-normal) var(--animation-easing-decelerate) both;
    transform: scale(1.02) translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    opacity: 1;
    border-color: var(--color-theme-primary-400);
    filter: brightness(1.03);
    transition: all var(--animation-duration-normal) var(--animation-easing-decelerate);
    will-change: transform;
    backface-visibility: hidden;
    -webkit-font-smoothing: subpixel-antialiased;
}}

/* 标题动画 */
.{self.unique_class} .title-1, .{self.unique_class} .title-2, .{self.unique_class} .title-3 {{
    animation: var(--animation-duration-normal) var(--animation-easing-decelerate) both;
    animation-name: {animations.get('entrance', {}).get('name', 'none')};
    animation-delay: calc(var(--animation-duration-fast) * 0.5);
    background: linear-gradient(135deg, var(--color-theme-primary-200), var(--color-theme-primary-400));
    border-radius: 8px;
    opacity: 0.95;
}}
"""

        # 添加块样式规则
        block_style = self.style_rules.get("block_style", {})
        block_css = self._generate_block_css_rules(block_style)
        
        # 合并所有CSS规则
        return "\n".join(keyframes_rules) + animation_css + self._generate_base_css_rules() + block_css
    
    def _generate_base_css_rules(self) -> str:
        """生成基础CSS规则"""
        base_css = f"""
/* 基础样式 */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}


body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
    background: #FFFFFF;
    padding: 0px;
    overflow: auto;
}}


/* 卡片容器 */
.{self.unique_class} .card {{
    background: var(--color-layout-card-background);
    border: 1px solid var(--color-layout-card-border);
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
    position: relative;
    overflow: visible;
}}

/* 块级元素 */
.{self.unique_class} .block {{
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 8px;
    padding: var(--spacing-block-padding);
    overflow: auto;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}}

.{self.unique_class} .block:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}}

/* 子区块 */
.{self.unique_class} .subsection {{
    background: var(--color-component-subsection-background);
    border: 1px solid var(--color-component-subsection-border);
    border-radius: 12px;
    padding: var(--spacing-subsection-padding);
    margin: var(--spacing-subsection-margin_top) 0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}}

.{self.unique_class} .subsection::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, 
        var(--color-theme-accent-300) 0%, 
        var(-color-theme-accent-500) 100%);
    opacity: 0.7;
}}

/* 标题样式 */
.{self.unique_class} .title-1 {{
    background: var(--color-component-title_background-h1);
    color: var(--color-typography-title-h1);
    font-size: var(--font-size-h1);
    line-height: 1.2;
    font-weight: 700;
    margin-bottom: var(--spacing-md);
    text-align: center;
    padding: var(--spacing-sm);
    border-radius: 8px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    animation: fadeIn 1s ease-out;
}}

.{self.unique_class} .title-1::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.2) 0%, 
        rgba(255, 255, 255, 0) 50%, 
        rgba(255, 255, 255, 0.1) 100%);
    z-index: 1;
}}

.{self.unique_class} .title-2 {{
    background: var(--color-component-title_background-h2);
    color: var(--color-typography-title-h2);
    font-size: var(--font-size-h2);
    line-height: 1.3;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 6px;
    position: relative;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    animation: fadeIn 1s ease-out;
}}

.{self.unique_class} .title-2::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 10%;
    width: 80%;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--color-theme-primary-600) 50%, 
        transparent 100%);
}}

.{self.unique_class} .title-3 {{
    background: var(--color-component-title_background-h3);
    color: var(--color-typography-title-h3);
    font-size: var(--font-size-h3);
    line-height: 1.4;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
    border-left: 3px solid var(--color-theme-accent-500);
    animation: fadeIn 1s ease-out;
}}


@keyframes fadeIn {{
    0% {{
        opacity: 0;
        transform: translateY(10px);
    }}
    100% {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.{self.unique_class} .title-4 {{
    background: var(--color-component-title_background-h4);
    color: var(--color-typography-title-h4);
    font-size: var(--font-size-h4);
    line-height: 1.5;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
    border-bottom: 1px solid var(--color-theme-secondary-300);
}}

/* 内容区域 */
.{self.unique_class} .content {{
    background: var(--color-component-content-background);
    color: var(--color-typography-text-primary);
    font-size: var(--font-size-body);
    line-height: 1.6;
    padding: var(--spacing-sm);
    border-radius: 4px;
    position: relative;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}}

.{self.unique_class} .content p {{
    margin-bottom: var(--spacing-sm);
    position: relative;
    z-index: 1;
}}

.{self.unique_class} .content p:last-child {{
    margin-bottom: 0;
}}


/* 图片样式 */
.{self.unique_class} .image-wrapper {{
    margin: var(--spacing-xs) 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}}

.{self.unique_class} .image-wrapper:hover {{
    transform: scale(1.02);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}}

.{self.unique_class} .content-image {{
    max-width: 100%;
    height: auto;
    display: block;
    object-fit: contain;
    margin: 0 auto;
    transition: all 0.5s ease;
}}

.{self.unique_class} .content-image:hover {{
    filter: brightness(1.05);
}}

.{self.unique_class} .link-wrapper {{
    margin: 0px;
    display: inline-block;
    position: relative;
}}

.{self.unique_class} .link {{
    color: var(--color-theme-primary-600);
    text-decoration: none;
    background: linear-gradient(90deg, 
        var(--color-theme-primary-500), 
        var(--color-theme-accent-500));
    -webkit-background-clip: text;
    color: transparent;
    transition: all 0.3s ease;
    position: relative;
}}

.{self.unique_class} .link:hover {{
    background: linear-gradient(90deg, 
        var(--color-theme-accent-500), 
        var(--color-theme-primary-500));
    -webkit-background-clip: text;
    transform: translateY(-1px);
}}

.{self.unique_class} .link::after {{
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, 
        var(--color-theme-primary-300), 
        var(--color-theme-accent-300));
    transform: scaleX(0);
    transform-origin: right;
    transition: transform 0.3s ease;
}}

.{self.unique_class} .link:hover::after {{
    transform: scaleX(1);
    transform-origin: left;
}}

/* 代码块 */
.{self.unique_class} .code-block {{
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 6px;
    padding: var(--spacing-sm);
    margin: var(--spacing-md) 0;
    overflow-x: auto;
    position: relative;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}}

.{self.unique_class} .code-block::before {{
    content: 'Code';
    position: absolute;
    top: -10px;
    left: 10px;
    background: var(--color-theme-primary-500);
    color: white;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    z-index: 1;
}}

/* 表格样式 */
.{self.unique_class} .table-wrapper,
.{self.unique_class} .table-container {{
    margin: var(--spacing-md) 0;
    overflow-x: auto;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}}

.{self.unique_class} .table-wrapper table,
.{self.unique_class} table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--color-component-content-background);
    border-radius: 8px;
    overflow: hidden;
}}

.{self.unique_class} table th, 
.{self.unique_class} table td,
.{self.unique_class} .table-wrapper th, 
.{self.unique_class} .table-wrapper td {{
    padding: var(--spacing-xs) var(--spacing-sm);
    border: 1px solid var(--color-layout-block-border);
    text-align: left;
    transition: all 0.2s ease;
}}

.{self.unique_class} table th,
.{self.unique_class} .table-wrapper th {{
    background: var(--color-theme-primary-100);
    font-weight: 600;
    color: var(--color-typography-title-h3);
    position: relative;
}}

.{self.unique_class} table th::after,
.{self.unique_class} .table-wrapper th::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: var(--color-theme-primary-300);
}}

.{self.unique_class} table tr:nth-child(even),
.{self.unique_class} .table-wrapper tr:nth-child(even) {{
    background-color: var(--color-theme-primary-50);
}}

.{self.unique_class} table tr:hover,
.{self.unique_class} .table-wrapper tr:hover {{
    background-color: var(--color-theme-secondary-50);
}}

.{self.unique_class} table td,
.{self.unique_class} .table-wrapper td {{
    color: var(--color-typography-text-primary);
}}

.{self.unique_class} ul {{
    list-style-position: inside;
    margin-left: var(--spacing-sm);
    padding-left: 20px;
}}

.{self.unique_class} ol {{
    list-style-type: none;
    counter-reset: item;
    margin-left: var(--spacing-sm);
    padding-left: 20px;
}}

.{self.unique_class} li {{
    margin: var(--spacing-xs) 0;
    position: relative;
    padding-left: var(--spacing-sm);
}}

/* 无序列表样式 */
.{self.unique_class} ul li::before {{
    content: '•';
    color: var(--color-theme-accent-500);
    font-weight: bold;
    display: inline-block;
    width: 1em;
    margin-left: -1em;
}}

/* 有序列表样式 */
.{self.unique_class} ol > li {{
    counter-increment: item;
    display: block;
    position: relative;
}}

.{self.unique_class} ol > li::before {{
    content: counter(item) ".";
    color: var(--color-theme-primary-500);
    font-weight: bold;
    position: absolute;
    left: -20px;
}}

/* 嵌套列表样式 */
.{self.unique_class} ol ol {{
    counter-reset: subitem;
    margin-top: var(--spacing-xs);
    margin-left: 20px;
}}

.{self.unique_class} ol ol > li {{
    counter-increment: subitem;
}}

.{self.unique_class} ol ol > li::before {{
    content: counter(item) "." counter(subitem);
    left: -25px;
}}

/* 动画和过渡效果 */
.{self.unique_class} * {{
    transition: all 0.3s ease;
}}

@keyframes pulse {{
    0% {{
        box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.4);
    }}
    70% {{
        box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
    }}
    100% {{
        box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
    }}
}}

/* 响应式调整 */
@media (max-width: 768px) {{
    .{self.unique_class} .block {{
        padding: var(--spacing-xs);
    }}
    
    .{self.unique_class} .title-1 {{
        font-size: calc(var(--font-size-h1) * 0.9);
    }}
    
    .{self.unique_class} .title-2 {{
        font-size: calc(var(--font-size-h2) * 0.9);
    }}
}}
"""
        
        return base_css

    def _generate_block_css_rules(self, block_style) -> str:
        """生成块样式CSS规则"""
        if not block_style or "css" not in block_style:
            return ""
        
        css = block_style["css"]
        
        block_css = f"""
/* 块级元素增强样式 */
.{self.unique_class} .block {{
    border-radius: {css.get("border-radius", "8px")};
    border-width: {css.get("border-width", "1px")};
    border-style: {css.get("border-style", "solid")};
    border-color: {css.get("border-color", "var(--color-layout-block-border)")};
    background: {css.get("background", "var(--color-layout-block-background)")};
    padding: {css.get("padding", "var(--spacing-md)")};
    box-shadow: {css.get("box-shadow", "0 4px 8px rgba(0, 0, 0, 0.05)")};
    opacity: {css.get("opacity", "1")};
    transition: {css.get("transition", "all 0.3s ease")};
    {css.get("dynamic_light", "")}
}}

.{self.unique_class} .block:hover {{
    {css.get("hover_effect", "")}
}}
"""
        
        return block_css
