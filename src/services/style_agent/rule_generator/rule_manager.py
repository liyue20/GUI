from typing import Dict, Any, Optional
from .config import ColorConfig, SpacingConfig, TypographyConfig, AnimationConfig
from .generators import ColorGenerator, SpacingGenerator, TypographyGenerator, AnimationGenerator
from .utils.style_preset_manager import StylePresetManager
from .generators.block_style_generator import BlockStyleGenerator
from .config.block_style_config import BlockStyleConfig
class StyleRuleGenerator:
    """样式规则生成器"""
    
    def __init__(self, layout_info: Dict[str, Any], card_size: Dict[str, int], 
                 theme_color: Optional[str] = None,
                 color_preset: Optional[str] = None,
                 typography_preset: Optional[str] = None,
                 spacing_preset: Optional[str] = None):
        """
        初始化样式规则生成器
        
        Args:
            layout_info: 布局信息，包含各个布局块的位置和尺寸信息
            card_size: 卡片尺寸 {'width': int, 'height': int}
            theme_color: 可选的主题色
            color_preset: 可选的颜色预设名称
            typography_preset: 可选的排版预设名称
            spacing_preset: 可选的间距预设名称
        """
        # 验证并设置默认值
        if not isinstance(layout_info, dict):
            layout_info = {}
        
        # 添加默认的布局密度设置
        self.style_config = {
            'density': 'comfortable',
            'text_density': 'comfortable'
        }
        
        # 保存原始布局信息
        self.layout_info = layout_info
        
        if not isinstance(card_size, dict) or 'width' not in card_size or 'height' not in card_size:
            card_size = {'width': 1200, 'height': 800}
        
        self.card_size = card_size
        
        # 初始化配置
        self.color_config = ColorConfig(theme_color, color_preset)
        self.spacing_config = SpacingConfig(spacing_preset)
        self.typography_config = TypographyConfig(typography_preset)
        self.animation_config = AnimationConfig()
        # 初始化生成器
        self.color_generator = ColorGenerator(self.color_config)
        self.spacing_generator = SpacingGenerator(self.spacing_config, self.typography_config.TYPOGRAPHY_SYSTEM['base_size'])
        self.typography_generator = TypographyGenerator(self.typography_config)
        self.animation_generator = AnimationGenerator(self.animation_config)
        self.block_style_generator = BlockStyleGenerator(BlockStyleConfig())

    def generate(self) -> Dict[str, Any]:
        """生成完整的样式规则"""
        try:
            # 先验证所有配置
            color_validation = self.color_config.validate()
            spacing_validation = self.spacing_config.validate()
            typography_validation = self.typography_config.validate()
            
            # 收集所有验证错误
            all_errors = []
            if not color_validation.is_valid:
                all_errors.extend(["颜色配置错误:"] + color_validation.errors)
            if not spacing_validation.is_valid:
                all_errors.extend(["间距配置错误:"] + spacing_validation.errors)
            if not typography_validation.is_valid:
                all_errors.extend(["排版配置错误:"] + typography_validation.errors)
                
            # 如果有误，抛出异常
            if all_errors:
                raise ValueError("\n".join(all_errors))
                
            # 验证通过，继续生成规则
            color_rules = self.color_generator.generate(self.layout_info)
            spacing_rules = self.spacing_generator.generate(self.layout_info)
            typography_rules = self.typography_generator.generate(self.layout_info)
            block_style = self.block_style_generator.generate(self.layout_info)
            #返回新的随机样式规则库
            css_lab = self.block_style_generator.load_css()
            # 生成动效规则
            animation_rules = self.animation_generator.generate(self.layout_info)
            
            return {
                "color": color_rules,
                "spacing": spacing_rules,
                "typography": typography_rules,
                "animation": animation_rules,
                "block_style": block_style,
                "css_lab": css_lab
            }
            
        except Exception as e:
            raise RuntimeError(f"生成样式规则失败: {str(e)}")
    
    def generate_css_variables(self) -> Dict[str, str]:
        """生成CSS变量"""
        rules = self.generate()
        css_vars = {}
        
        # 处理颜色变量
        color_rules = rules["color"]
        
        # 处理主题色变量
        for scale, color in color_rules["theme"]["primary"].items():
            css_vars[f"--color-primary-{scale}"] = color
        
        # 处理布局颜色变量
        for layout, values in color_rules["layout"].items():
            for key, color in values.items():
                css_vars[f"--color-layout-{layout}-{key}"] = color
        
        # 处理组件颜色变量
        for component, values in color_rules["component"].items():
            for key, color in values.items():
                css_vars[f"--color-component-{component}-{key}"] = color
        
        # 处理文本颜色变量
        for category, values in color_rules["typography"].items():
            for key, color in values.items():
                css_vars[f"--color-typography-{category}-{key}"] = color
        
        # 处理间距变量
        spacing_rules = rules["spacing"]
        
        # 基础间距变量
        for name, value in spacing_rules["scale"].items():
            css_vars[f"--spacing-{name}"] = f"{value}px"
        
        # 布局间距变量
        for component, values in spacing_rules["layout"].items():
            for key, value in values.items():
                css_vars[f"--spacing-{component}-{key}"] = f"{value}px"
        
        # 处理排版变量
        typography_rules = rules["typography"]
        
        # 字体大小变量
        for name, size in typography_rules["sizes"].items():
            css_vars[f"--font-size-{name}"] = f"{size}px"
        
        # 文本样式变量
        for style_name, style in typography_rules["styles"].items():
            css_vars[f"--font-size-{style_name}"] = f"{style['font_size']}px"
            css_vars[f"--line-height-{style_name}"] = str(style['line_height'])
            css_vars[f"--font-weight-{style_name}"] = str(style['font_weight'])
        
        return css_vars
    
    def generate_css(self) -> str:
        """生成完整的CSS代码"""
        css_vars = self.generate_css_variables()
        
        # 生成CSS变量声明
        css = ":root {\n"
        for name, value in css_vars.items():
            css += f"  {name}: {value};\n"
        css += "}\n\n"
        
        # 生成基础样式
        card_width = self.card_size['width']
        card_height = self.card_size['height']
        
        css += f"""
/* 基础样式 */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
    background: #f5f5f5;
    padding: 20px;
}}

/* 卡片容器 */
.card {{
    width: {card_width}px;
    height: {card_height}px;
    position: relative;
    overflow: hidden;
    background: var(--color-layout-card-background);
    border: 1px solid var(--color-layout-card-border);
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}}

/* 块级元素 */
.block {{
    position: absolute;
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 8px;
    padding: var(--spacing-block-padding);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    overflow-y: auto; 
    overflow-x: hidden;
}}

/* 子区块 */
.subsection {{
    background: var(--color-component-subsection-background);
    border: 1px solid var(--color-component-subsection-border);
    border-radius: 6px;
    padding: var(--spacing-subsection-padding);
    margin: var(--spacing-subsection-margin_top) 0;
    overflow: auto;
}}

/* 标题样式 */
.title-1 {{
    background: var(--color-component-title_background-h1);
    color: var(--color-typography-title-h1);
    font-size: var(--font-size-h1);
    line-height: var(--line-height-h1);
    font-weight: var(--font-weight-h1);
    margin-bottom: var(--spacing-md);
    padding: var(--spacing-sm);
    text-align: center;
    border-radius: 6px;
}}

.title-2 {{
    background: var(--color-component-title_background-h2);
    color: var(--color-typography-title-h2);
    font-size: var(--font-size-h2);
    line-height: var(--line-height-h2);
    font-weight: var(--font-weight-h2);
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
}}

.title-3 {{
    background: var(--color-component-title_background-h3);
    color: var(--color-typography-title-h3);
    font-size: var(--font-size-h3);
    line-height: var(--line-height-h3);
    font-weight: var(--font-weight-h3);
    margin-bottom: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
}}

/* 内部区域 */
.content {{
    background: var(--color-component-content-background);
    color: var(--color-typography-text-primary);
    font-size: var(--font-size-body);
    line-height: var(--line-height-body);
    font-weight: var(--font-weight-body);
    padding: var(--spacing-sm);
    border-radius: 4px;
}}

/* 辅助文本 */
.caption {{
    color: var(--color-typography-text-secondary);
    font-size: var(--font-size-caption);
    line-height: var(--line-height-caption);
    font-weight: var(--font-weight-caption);
}}

/* 图片容器 */
.image-wrapper {{
    margin: var(--spacing-md) 0;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.content-image {{
    display: block;
    width: 100%;
    height: auto;
}}
"""
        
        # 为每个布局块生成具体的CSS
        for block_id, block_info in self.layout_info.items():
            css += f"""
/* {block_id} 布局块 */
.{block_id} {{
    position: absolute;
    left: {block_info.get('x', 0)}px;
    top: {block_info.get('y', 0)}px;
    width: {block_info.get('width', 100)}px;
    height: {block_info.get('height', 100)}px;
    background: var(--color-layout-block-background);
    border: 1px solid var(--color-layout-block-border);
    border-radius: 8px;
    padding: var(--spacing-block-padding);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    overflow-y: auto;
    overflow-x: hidden;
}}
"""
        
        return css
    
    @classmethod
    def from_preset(cls, layout_info: Dict[str, Any], card_size: Dict[str, int], 
                   preset_name: Optional[str] = None) -> 'StyleRuleGenerator':
        """
        从预设创建样式生成器
        
        Args:
            layout_info: 布局信息，只需包含 'density' 和 'text_density' 字段
            card_size: 卡片尺寸
            preset_name: 预设名称，如果为None则随机选择预设
        """
        # 获取预设
        preset = (StylePresetManager.get_preset(preset_name) if preset_name 
                 else StylePresetManager.get_random_preset())
        
        # 创建生成器实例，使用预设中的配置
        return cls(
            layout_info=layout_info,  # 只传入布局信息
            card_size=card_size,
            color_preset=preset.color_preset,
            typography_preset=preset.typography_preset,
            spacing_preset=preset.spacing_preset
        )

# __init__.py
from .rule_manager import StyleRuleGenerator

__all__ = ['StyleRuleGenerator']