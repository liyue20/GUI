from .base_config import BaseConfig, ValidationResult

from typing import Dict, Any, List

class ColorConfig(BaseConfig):
    """颜色配置"""
    
    # 预设的主题色系统
    PRESET_COLOR_SYSTEMS = [
        {
            "name": "blue",
            "color": "#2196F3",
            "type": "primary"
        },
        {
            "name": "green",
            "color": "#4CAF50",
            "type": "success"
        },
        {
            "name": "purple",
            "color": "#9C27B0",
            "type": "accent"
        },
        {
            "name": "orange",
            "color": "#FF5722",
            "type": "warning"
        },
        {
            "name": "red",
            "color": "#F44336",
            "type": "error"
        },
        {
            "name": "teal",
            "color": "#009688",
            "type": "info"
        },
        {
            "name": "grey",
            "color": "#607D8B",
            "type": "neutral"
        }
    ]
    
    # 色板结构
    PALETTE_STRUCTURE = {
        # 主题色系列(用于生成其他颜色)
        "theme": {
            "primary": {
                "50": "",   # 最浅色
                "100": "", 
                "200": "",
                "300": "",
                "400": "",
                "500": "", # 主题色
                "600": "",
                "700": "",
                "800": "",
                "900": ""  # 最深色
            }
        },
        
        # 布局层级色系
        "layout": {
            "card": {
                "background": "",  # 最外层容器背景
                "border": ""      # 容器边框
            },
            "block": {
                "background": "", # block背景
                "border": ""     # block边框
            }
        },
        
        # 组件色系
        "component": {
            # 标题背景
            "title_background": {
                "h1": "",      # 一级标题背景
                "h2": "",      # 二级标题背景
                "h3": "",      # 三级标题背景
                "h4": "",      # 四级标题背景
                "h5": ""       # 五级标题背景
            },
            # 子区背景
            "subsection": {
                "background": "", # 子区块背景色
                "border": ""     # 子区块边框
            },
            # 内容区域背景
            "content": {
                "background": "" # 内容区域统一背景色
            }
        },
        
        # 文本色系
        "typography": {
            "title": {
                "h1": "",       # 一级标题文字色
                "h2": "",       # 二级标题文字色
                "h3": "",       # 三级标题文字色
                "h4": "",       # 四级标题文字色
                "h5": ""        # 五级标题文字色
            },
            "text": {
                "primary": "",    # 主要文本色
                "secondary": ""   # 次要文本色
            }
        }
    }
    
    # WCAG标准配置
    WCAG_STANDARDS = {
        "normal_text": 4.5,     # AA级正常文本
        "large_text": 3.0,      # AA级大号文本
        "ui_components": 3.0    # UI组件
    }

    def __init__(self, theme_color: str = None, preset_name: str = None):
        """
        初始化颜色配置
        Args:
            theme_color: 直接指定的主题色
            preset_name: 预设主题名称
        """
        if theme_color:
            self.theme_color = theme_color
        elif preset_name:
            preset = next((p for p in self.PRESET_COLOR_SYSTEMS if p["name"] == preset_name),
                         self.PRESET_COLOR_SYSTEMS[0])  # 默认使用 blue
            self.theme_color = preset["color"]
        else:
            import random
            preset = random.choice(self.PRESET_COLOR_SYSTEMS)
            self.theme_color = preset["color"]
    
    def validate(self) -> ValidationResult:
        """验证颜色配置"""
        errors = []
        
        # 1. 验证主题色格式
        if not self._validate_hex_color(self.theme_color):
            errors.append(f"无效的主题色格式: {self.theme_color}")
        
        # 2. 验证色板结构完整性
        required_keys = ["theme", "layout", "typography"]
        for key in required_keys:
            if key not in self.PALETTE_STRUCTURE:
                errors.append(f"缺少必需的色板结构: {key}")
        
        # 3. 验证WCAG标准配置
        if "normal_text" not in self.WCAG_STANDARDS:
            errors.append("缺少正常文本的WCAG标准配置")
        if "large_text" not in self.WCAG_STANDARDS:
            errors.append("缺少大号文本的WCAG标准配置")
            
        # 4. 验证颜色对比度
        contrast_errors = self._validate_contrast_ratios()
        errors.extend(contrast_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def _validate_hex_color(self, color: str) -> bool:
        """验证十六进制颜色格式"""
        if not color:
            return False
        if not color.startswith('#'):
            return False
        try:
            int(color[1:], 16)
            return len(color) in [4, 7]  # #RGB or #RRGGBB
        except ValueError:
            return False
    
    def _validate_contrast_ratios(self) -> List[str]:
        """验证颜色对比度"""
        errors = []
        
        # 这里需要实现具体的对比度验证
        # 1. 文本与背景的对比度
        # 2. 标题与背景的对比度
        # 3. 功能色与背景的对比度
        
        return errors