# runtime/converter/style_applier.py
import json
from typing import Dict, Any

class StyleApplier:
    """样式应用器"""
    
    def __init__(self, style_rules: Dict[str, Any]):
        self.style_rules = style_rules
    
    def apply(self, html: str) -> str:
        """应用样式生成完整HTML"""
        try:
            template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>aigui-generator-html</title>
    <style>
        /* CSS 变量 */
        {self._generate_css_variables()}
        
        /* CSS 规则 */
        {self._generate_css_rules()}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""
            return template
            
        except Exception as e:
            raise RuntimeError(f"应用样式失败: {str(e)}")
    
    def _generate_css_variables(self) -> str:
        """生成CSS变量声明"""
        css_vars = [":root {"]
        
        # 添加颜色变量
        for category, values in self.style_rules["color"].items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, dict):
                        for sub_key, color in value.items():
                            css_vars.append(f"    --color-{category}-{key}-{sub_key}: {color};")
                    else:
                        css_vars.append(f"    --color-{category}-{key}: {value};")
        
        # 添加间距变量
        spacing = self.style_rules.get("spacing", {})
        for key, value in spacing.get("scale", {}).items():
            css_vars.append(f"    --spacing-{key}: {value}px;")
        
        # 添加排版变量
        typography = self.style_rules.get("typography", {})
        for key, value in typography.get("sizes", {}).items():
            css_vars.append(f"    --font-size-{key}: {value}px;")
            
        css_vars.append("}")
        #with open("css_variables.json", "w", encoding="utf-8") as file:
        #      json.dump(css_vars, file, indent=2, ensure_ascii=False)
        return "\n".join(css_vars)
    
    def _generate_css_rules(self) -> str:
        """生成CSS规则"""
        return """
/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
    background: #FFFFFF;
    padding: 0px;
    overflow: auto;
}

/* 卡片容器 */
.card {
    background: var(--color-layout-card-background);
    border: 1px solid var(--color-layout-card-border);
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
}

/* 块级元素 */
.block {
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 8px;
    padding: var(--spacing-block-padding);
}

/* 子区块 */
.subsection {
    background: var(--color-component-subsection-background);
    border: 1px solid var(--color-component-subsection-border);
    border-radius: 6px;
    padding: var(--spacing-subsection-padding);
    margin: var(--spacing-subsection-margin_top) 0;
}

/* 标题样式 */
.title-1 {
    background: var(--color-component-title_background-h1);
    color: var(--color-typography-title-h1);
    font-size: var(--font-size-h1);
    line-height: 1.2;
    font-weight: 700;
    margin-bottom: var(--spacing-md);
    text-align: center;
    padding: var(--spacing-sm);
    border-radius: 6px;
}

.title-2 {
    background: var(--color-component-title_background-h2);
    color: var(--color-typography-title-h2);
    font-size: var(--font-size-h2);
    line-height: 1.3;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
}

.title-3 {
    background: var(--color-component-title_background-h3);
    color: var(--color-typography-title-h3);
    font-size: var(--font-size-h3);
    line-height: 1.4;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
}

/* 内容区域 */
.content {
    background: var(--color-component-content-background);
    color: var(--color-typography-text-primary);
    font-size: var(--font-size-body);
    line-height: 1.6;
    padding: var(--spacing-sm);
    border-radius: 4px;
}

.content p {
    margin-bottom: var(--spacing-sm);
}

.content p:last-child {
    margin-bottom: 0;
}

/* 图片样式 */
.image-wrapper {
    margin: var(--spacing-xs) 0;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.content-image {
    max-width: 100%;
    height: auto;
    display: block;
    object-fit: contain;
    margin: 0 auto;
}
.link-wrapper {
    margin: 0px;  /* 给链接加个间距 */
    display: inline-block;
}

.link {
    color: blue;
    text-decoration: underline;
}

.link:hover {
    color: darkblue;
}

/* 代码块 */
.code-block {
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 4px;
    padding: var(--spacing-sm);
    margin: var(--spacing-md) 0;
    overflow-x: auto;
}

/* 表格样式 */
.table-container {
    margin: var(--spacing-md) 0;
    overflow-x: auto;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
    background: var(--color-component-content-background);
}

th, td {
    padding: var(--spacing-xs);
    border: 1px solid var(--color-layout-block-border);
    text-align: left;
}

th {
    background: var(--color-layout-block-background);
    font-weight: 600;
    color: var(--color-typography-title-h3);
}

td {
    color: var(--color-typography-text-primary);
}
ul {
    list-style-position: inside;  
}

li {
    margin-left: 5px;  
}

"""