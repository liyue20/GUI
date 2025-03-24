# runtime/converter/style_applier.py
import json
import uuid
from typing import Dict, Any

class StyleApplier:
    """样式应用器"""
    
    def __init__(self, style_rules: Dict[str, Any], scale):
        self.style_rules = style_rules
        self.scale = scale

    def apply(self, html: str, scale) -> str:
        """应用样式生成完整HTML"""
        try:
            # 生成一个随机的类名
            class_name = self._generate_random_class_name()
            
            template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* CSS 变量 */
        {self._generate_css_variables(scale, class_name)}
        
        /* CSS 规则 */
        {self._generate_css_rules(class_name)}
    </style>
</head>
<body>
  <div class="{class_name}">
    {html}
    
    <!-- 全屏图片查看器 -->
    <div class="fullscreen-viewer" id="imageViewer">
      <img src="" class="fullscreen-image" id="viewerImage">
      <button class="close-button" id="closeViewer">×</button>
    </div>
  </div>
  
  <!-- 图片点击全屏查看功能的JavaScript -->
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      // 获取所有图片和查看器元素
      const imageWrappers = document.querySelectorAll('.{class_name} .image-wrapper');
      const viewer = document.getElementById('imageViewer');
      const viewerImage = document.getElementById('viewerImage');
      const closeButton = document.getElementById('closeViewer');
      
      // 为每个图片添加点击事件
      imageWrappers.forEach(wrapper => {{
        wrapper.addEventListener('click', function() {{
          const image = this.querySelector('.content-image');
          if (image) {{
            viewerImage.src = image.src;
            viewer.classList.add('active');
            document.body.style.overflow = 'hidden'; // 防止滚动
          }}
        }});
      }});
      
      // 关闭查看器
      closeButton.addEventListener('click', function() {{
        viewer.classList.remove('active');
        document.body.style.overflow = '';
      }});
      
      // 点击背景也可以关闭
      viewer.addEventListener('click', function(e) {{
        if (e.target === viewer) {{
          viewer.classList.remove('active');
          document.body.style.overflow = '';
        }}
      }});
      
      // ESC键关闭
      document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape' && viewer.classList.contains('active')) {{
          viewer.classList.remove('active');
          document.body.style.overflow = '';
        }}
      }});
    }});
  </script>
</body>
</html>
"""
            return template
            
        except Exception as e:
            raise RuntimeError(f"应用样式失败: {str(e)}")
    
    def _generate_random_class_name(self) -> str:
        """生成随机类名"""
        return f"class-{uuid.uuid4().hex[:8]}"  # 生成一个8位的随机类名

    def _generate_css_variables(self, scale, class_name: str) -> str:
        """生成CSS变量声明"""
        css_vars = [f".{class_name} {{"]
        
        # 添加颜色变量
        for category, values in self.style_rules["color"].items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, dict):
                        for sub_key, color in value.items():
                            css_vars.append(f"    --{class_name}-color-{category}-{key}-{sub_key}: {color};")
                    else:
                        css_vars.append(f"    --{class_name}-color-{category}-{key}: {value};")
        # 添加间距变量
        spacing = self.style_rules.get("spacing", {})
        for key, value in spacing.get("scale", {}).items():
            css_vars.append(f"    --{class_name}-spacing-{key}: {value*scale*0.8}px;")
        
        # 添加排版变量
        typography = self.style_rules.get("typography", {})
        for key, value in typography.get("sizes", {}).items():
            css_vars.append(f"    --{class_name}-font-size-{key}: {value*scale}px;")
            
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def _generate_css_rules(self, class_name: str) -> str:
        """生成CSS规则"""
        return f"""
/* 基础样式 */
.{class_name} * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

.{class_name} body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
    background: #FFFFFF;
    padding: 0px;
    overflow: auto;
}}

/* 卡片容器 */
.{class_name} .card {{
    background: var(--{class_name}-color-layout-card-background);
    border: 1px solid var(--{class_name}-color-layout-card-border);
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
}}

/* 块级元素 */
.{class_name} .block {{
    background: var(--{class_name}-color-layout-block-background);
    border: 1px solid var(--{class_name}-color-layout-block-border);
    border-radius: 8px;
    padding: var(--{class_name}-spacing-block-padding);
    overflow: auto;
}}
.{class_name} .block:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}}

/* 子区块 */
.{class_name} .subsection {{
    background: var(--{class_name}-color-component-subsection-background);
    border: 1px solid var(--{class_name}-color-component-subsection-border);
    border-radius: 12px;
    padding: var(--{class_name}-spacing-subsection-padding);
    margin: var(--{class_name}-spacing-subsection-margin_top) 0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}}

/* 标题样式 */
.{class_name} .title-1 {{
    background: var(--{class_name}-color-component-title_background-h1);
    color: var(--{class_name}-color-typography-title-h1);
    font-size: var(--{class_name}-font-size-h1);
    line-height: 1.2;
    font-weight: 700;
    margin-bottom: var(--{class_name}-spacing-md);
    text-align: center;
    padding: var(--{class_name}-spacing-sm);
    border-radius: 6px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    animation: fadeIn 1s ease-out;
}}

.{class_name} .title-2 {{
    background: var(--{class_name}-color-component-title_background-h2);
    color: var(--{class_name}-color-typography-title-h2);
    font-size: var(--{class_name}-font-size-h2);
    line-height: 1.3;
    font-weight: 600;
    margin-bottom: var(--{class_name}-spacing-sm);
    padding: var(--{class_name}-spacing-xs) var(--{class_name}-spacing-sm);
    border-radius: 4px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    animation: fadeIn 1s ease-out;
}}

.{class_name} .title-3 {{
    background: var(--{class_name}-color-component-title_background-h3);
    color: var(--{class_name}-color-typography-title-h3);
    font-size: var(--{class_name}-font-size-h3);
    line-height: 1.4;
    font-weight: 600;
    margin-bottom: var(--{class_name}-spacing-sm);
    padding: var(--{class_name}-spacing-xs) var(--{class_name}-spacing-sm);
    border-radius: 4px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    animation: fadeIn 1s ease-out;
}}

@keyframes fadeIn {{
    0% {{
        opacity: 0;
    }}
    100% {{
        opacity: 1;
    }}
}}

.{class_name} .title-4 {{
    background: var(--{class_name}-color-component-title_background-h4);
    color: var(--{class_name}-color-typography-title-h4);
    font-size: var(--{class_name}-font-size-h4);
    line-height: 1.5;
    font-weight: 600;
    margin-bottom: var(--{class_name}-spacing-sm);
    padding: var(--{class_name}-spacing-xs) var(--{class_name}-spacing-sm);
    border-radius: 4px;
}}

/* 内容区域 */
.{class_name} .content {{
    background: var(--{class_name}-color-component-content-background);
    color: var(--{class_name}-color-typography-text-primary);
    font-size: var(--{class_name}-font-size-body);
    line-height: 1.6;
    padding: var(--{class_name}-spacing-sm);
    border-radius: 4px;
}}

.{class_name} .content p {{
    margin-bottom: var(--{class_name}-spacing-sm);
    display: block;
}}

.{class_name} .content p:last-child {{
    margin-bottom: 0;
}}

/* 图片样式 */
.{class_name} .image-wrapper {{
    margin: var(--{class_name}-spacing-xs) 0;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    cursor: pointer; /* 添加指针样式，提示可点击 */
    position: relative;
}}

.{class_name} .image-wrapper::after {{
    content: '🔍';
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    padding: 5px;
    border-radius: 4px;
    font-size: 14px;
    opacity: 0;
    transition: opacity 0.3s;
}}

.{class_name} .image-wrapper:hover::after {{
    opacity: 1;
}}

.{class_name} .content-image {{
    max-width: 100%;
    height: auto;
    display: block;
    object-fit: contain;
    margin: 0 auto;
    transition: transform 0.3s ease;
}}

/* 全屏查看器样式 */
.{class_name} .fullscreen-viewer {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.9);
    z-index: 1000;
    justify-content: center;
    align-items: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}}

.{class_name} .fullscreen-viewer.active {{
    display: flex;
    opacity: 1;
}}

.{class_name} .fullscreen-image {{
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}}

.{class_name} .close-button {{
    position: absolute;
    top: 20px;
    right: 20px;
    color: white;
    background: rgba(0, 0, 0, 0.5);
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: background 0.3s;
}}

.{class_name} .close-button:hover {{
    background: rgba(255, 0, 0, 0.7);
}}

.{class_name} .link-wrapper {{
    margin: 0px;  /* 给链接加个间距 */
    display: inline-block;
}}

.{class_name} .link {{
    color: #1e90ff;
    text-decoration: none;
    background: linear-gradient(45deg, #1e90ff, #00bfff);
    -webkit-background-clip: text;
    color: transparent;
}}

.{class_name} .link:hover {{
    background: linear-gradient(45deg, #00bfff, #1e90ff);
}}


/* 代码块 */
.{class_name} .code-block {{
    background: var(--{class_name}-color-layout-block-background);
    border: 1px solid var(--{class_name}-color-layout-block-border);
    border-radius: 4px;
    padding: var(--{class_name}-spacing-sm);
    margin: var(--{class_name}-spacing-md) 0;
    overflow-x: auto;
}}

/* 表格样式 */
.{class_name} .table-container {{
    margin: var(--{class_name}-spacing-md) 0;
    overflow-x: auto;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.{class_name} table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--{class_name}-color-component-content-background);
}}

.{class_name} th, .{class_name} td {{
    padding: var(--{class_name}-spacing-xs);
    border: 1px solid var(--{class_name}-color-layout-block-border);
    text-align: left;
}}

.{class_name} th {{
    background: var(--{class_name}-color-layout-block-background);
    font-weight: 600;
    color: var(--{class_name}-color-typography-title-h3);
}}

.{class_name} td {{
    color: var(--{class_name}-color-typography-text-primary);
}}
.{class_name} ul {{
    list-style-position: inside;  
}}

.{class_name} li {{
    margin-left: 5px;  
}}
.{class_name} * {{
    transition: all 0.3s ease;
}}

/* 列表样式 */
.{class_name} ul, .{class_name} ol {{
    padding-left: var(--{class_name}-spacing-md);
    margin: var(--{class_name}-spacing-xs) 0;
    list-style-position: outside;
}}

.{class_name} li {{
    margin: var(--{class_name}-spacing-xxs) 0;
    padding-left: var(--{class_name}-spacing-xs);
}}

/* 嵌套列表样式 */
.{class_name} li > ul,
.{class_name} li > ol {{
    margin-top: var(--{class_name}-spacing-xs);
    margin-bottom: var(--{class_name}-spacing-xs);
}}

/* 有序列表样式 */
.{class_name} ol {{
    list-style-type: decimal;
}}

/* 无序列表样式 */
.{class_name} ul {{
    list-style-type: disc;
}}

/* 二级列表样式 */
.{class_name} ul ul {{
    list-style-type: circle;
}}
.{class_name} ol ol {{
    list-style-type: lower-alpha;
}}

/* 三级列表样式 */
.{class_name} ul ul ul {{
    list-style-type: square;
}}
.{class_name} ol ol ol {{
    list-style-type: lower-roman;
}}

"""
