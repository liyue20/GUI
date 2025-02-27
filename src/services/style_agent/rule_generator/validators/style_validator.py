from typing import Dict, Any
from ..config import ColorConfig, TypographyConfig, SpacingConfig
from ...utils.color_utils import ColorUtils

class StyleValidator:
    """样式验证器"""
    
    def __init__(self):
        self.color_utils = ColorUtils()
    
    def validate_style(self, style: Dict[str, Any]) -> bool:
        """
        验证完整样式
        
        Args:
            style: 完整的样式配置
            
        Returns:
            bool: 验证结果
        """
        try:
            # 验证颜色
            if not self._validate_colors(style.get('colors', {})):
                return False
                
            # 验证字体
            if not self._validate_typography(style.get('typography', {})):
                return False
                
            # 验证间距
            if not self._validate_spacing(style.get('spacing', {})):
                return False
            
            return True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False
    
    def _validate_colors(self, colors: Dict) -> bool:
        """验证颜色配置"""
        try:
            # 验证必要的颜色键是否存在
            required_colors = {
                'page': ['background', 'content'],
                'module': ['primary', 'secondary', 'light'],
                'text': ['primary', 'secondary', 'hint']
            }
            
            for section, keys in required_colors.items():
                if section not in colors:
                    print(f"Missing color section: {section}")
                    return False
                    
                for key in keys:
                    if key not in colors[section]:
                        print(f"Missing color key: {key} in section {section}")
                        return False
            
            # 验证对比度
            # 文本与背景对比度
            text_bg_contrast = self.color_utils.calculate_contrast(
                colors['text']['primary'],
                colors['page']['background']
            )
            if text_bg_contrast < 4.5:  # WCAG AA 标准
                print(f"Insufficient text-background contrast: {text_bg_contrast}")
                return False
            
            # 模块文本与背景对比度
            for module_type in ['primary', 'secondary', 'light']:
                module_contrast = self.color_utils.calculate_contrast(
                    colors['module'][module_type]['text'],
                    colors['module'][module_type]['background']
                )
                if module_contrast < 4.5:
                    print(f"Insufficient contrast in module {module_type}: {module_contrast}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Color validation error: {str(e)}")
            return False
    
    def _validate_typography(self, typography: Dict) -> bool:
        """验证字体配置"""
        try:
            required_elements = ['h1', 'h2', 'h3', 'h4', 'body', 'small', 'caption']
            required_props = ['size', 'weight', 'lineHeight']
            
            # 检查必要的元素和属性
            for element in required_elements:
                if element not in typography:
                    print(f"Missing typography element: {element}")
                    return False
                    
                for prop in required_props:
                    if prop not in typography[element]:
                        print(f"Missing typography property: {prop} in element {element}")
                        return False
            
            # 验证字体大小梯度
            sizes = {
                element: float(typography[element]['size'].replace('px', ''))
                for element in required_elements
            }
            
            # 验证标题梯度
            if not (sizes['h1'] > sizes['h2'] > sizes['h3'] > sizes['h4']):
                print("Invalid heading size gradient")
                return False
            
            # 验证正文大小关系
            if not (sizes['body'] >= sizes['small'] >= sizes['caption']):
                print("Invalid body text size relationship")
                return False
            
            return True
            
        except Exception as e:
            print(f"Typography validation error: {str(e)}")
            return False
    
    def _validate_spacing(self, spacing: Dict) -> bool:
        """验证间距配置"""
        try:
            # 验证基础间距
            required_scales = ['2xs', 'xs', 'sm', 'md', 'lg', 'xl', '2xl']
            for scale in required_scales:
                if scale not in spacing:
                    print(f"Missing spacing scale: {scale}")
                    return False
            
            # 验证组件间距
            required_components = [
                'component_section_gap',
                'component_title_gap',
                'component_paragraph_gap',
                'component_element_gap'
            ]
            for component in required_components:
                if component not in spacing:
                    print(f"Missing component spacing: {component}")
                    return False
            
            # 验证间距递增关系
            scales = {
                scale: float(spacing[scale].replace('px', ''))
                for scale in required_scales
            }
            
            previous = -1
            for scale in required_scales:
                current = scales[scale]
                if current <= previous:
                    print(f"Invalid spacing scale relationship at {scale}")
                    return False
                previous = current
            
            return True
            
        except Exception as e:
            print(f"Spacing validation error: {str(e)}")
            return False