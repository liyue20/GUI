from .base_config import BaseConfig, ValidationResult

class SpacingConfig(BaseConfig):
    """间距配置"""
    
    # 添加预设的间距系统
    PRESET_SPACING_SYSTEMS = [
        {
            "name": "compact",
            "base_unit": 4,
            "scales": {
                "xxs": 0.5,    # 2px
                "xs": 1,       # 4px
                "sm": 2,       # 8px
                "md": 3,       # 12px
                "lg": 4,       # 16px
                "xl": 6,       # 24px
                "xxl": 8       # 32px
            }
        },
        {
            "name": "balanced",
            "base_unit": 8,
            "scales": {
                "xxs": 0.5,    # 4px
                "xs": 1,       # 8px
                "sm": 1.5,     # 12px
                "md": 2,       # 16px
                "lg": 3,       # 24px
                "xl": 4,       # 32px
                "xxl": 6       # 48px
            }
        },
        {
            "name": "spacious",
            "base_unit": 12,
            "scales": {
                "xxs": 0.5,    # 6px
                "xs": 1,       # 12px
                "sm": 1.5,     # 18px
                "md": 2,       # 24px
                "lg": 3,       # 36px
                "xl": 4,       # 48px
                "xxl": 6       # 72px
            }
        }
    ]
    
    def __init__(self, preset_name: str = None):
        """
        初始化间距配置
        Args:
            preset_name: 预设名称，如果为None则随机选择
        """
        if preset_name is None:
            import random
            preset = random.choice(self.PRESET_SPACING_SYSTEMS)
        else:
            preset = next((p for p in self.PRESET_SPACING_SYSTEMS if p["name"] == preset_name),
                         self.PRESET_SPACING_SYSTEMS[1])  # 默认使用 balanced
            
        self.SPACING_SYSTEM = {
            "base_unit": preset["base_unit"],
            "scales": preset["scales"]
        }
    
    # 布局间距规则
    LAYOUT_SPACING = {
        "card": {
            "padding": "md"
        },
        "block": {
            "margin": "md",
            "padding": "sm"
        },
        "subsection": {
            "margin_top": "sm",
            "margin_bottom": "sm",
            "padding": "xs"
        }
    }
    
    def validate(self) -> ValidationResult:
        """验证间距配置"""
        errors = []
        
        # 1. 验证基础单位
        base_unit = self.SPACING_SYSTEM.get("base_unit")
        if base_unit is None:
            errors.append("缺少基础单位配置")
        elif base_unit < 2 or base_unit > 16:
            errors.append(f"基础单位 {base_unit}px 超出合理范围 (2-16px)")
            
        # 2. 验证梯度系列
        if "scales" not in self.SPACING_SYSTEM:
            errors.append("缺少间距梯度配置")
        else:
            scales = self.SPACING_SYSTEM["scales"]
            # 验证必需的梯度级别
            required_scales = ["xxs", "xs", "sm", "md", "lg", "xl", "xxl"]
            for scale in required_scales:
                if scale not in scales:
                    errors.append(f"缺少必需的间距级别: {scale}")
            
            # 验证梯度值的递增性
            prev_value = 0
            for name, value in scales.items():
                if value <= prev_value and name != "xxs":  # xxs可以最小
                    errors.append(f"间距梯度 {name} 未保持递增")
                prev_value = value
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )