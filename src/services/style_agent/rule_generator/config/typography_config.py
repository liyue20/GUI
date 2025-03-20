from .base_config import BaseConfig, ValidationResult

class TypographyConfig(BaseConfig):
    """排版配置"""
    
    # 添加预设的排版系统
    PRESET_TYPOGRAPHY_SYSTEMS = [
        {
            "name": "compact",
            "ratio": 1.125,     # 更小的比例
            "base_size": 12,    # 更小的基础字号
            "scales": {
                "caption": 0.833,  # 10px
                "body": 1,        # 12px
                "subtitle": 1.167, # 14px
                "title": 1.3,   # 16px
                "h4": 1.333,       # 16px
                "h3": 1.5,       # 18px
                "h2": 1.667,     # 20px
                "h1": 2.0,       # 24px
                "display": 2.333  # 28px
            }
        },
        {
            "name": "comfortable",
            "ratio": 1.2,       # 当前的比例
            "base_size": 14,    # 当前的基础字号
            "scales": {
                "caption": 0.857,  # 12px
                "body": 1,         # 14px
                "subtitle": 1.143, # 16px
                "title": 1.2,    # 18px
                "h4": 1.286,       # 18px
                "h3": 1.429,      # 20px
                "h2": 1.714,      # 24px
                "h1": 2.0,        # 28px
                "display": 2.286   # 32px
            }
        },
        {
            "name": "spacious",
            "ratio": 1.333,     # 更大的比例
            "base_size": 16,    # 更大的基础字号
            "scales": {
                "caption": 0.75,   # 12px
                "body": 1,         # 16px
                "subtitle": 1.25,  # 20px
                "title": 1.4,      # 24px
                "h4": 1.5,         # 24px
                "h3": 1.75,       # 28px
                "h2": 1.8,          # 32px
                "h1": 2.0,       # 36px
                "display": 2.5     # 40px
            }
        }
    ]
    
    def __init__(self, preset_name: str = None):
        """
        初始化排版配置
        Args:
            preset_name: 预设名称，如果为None则随机选择
        """
        if preset_name is None:
            import random
            preset = random.choice(self.PRESET_TYPOGRAPHY_SYSTEMS)
        else:
            preset = next((p for p in self.PRESET_TYPOGRAPHY_SYSTEMS if p["name"] == preset_name), 
                         self.PRESET_TYPOGRAPHY_SYSTEMS[1])  # 默认使用 comfortable
            
        self.TYPOGRAPHY_SYSTEM = {
            "ratio": preset["ratio"],
            "base_size": preset["base_size"],
            "scales": preset["scales"],
            "line_height": {
                "tight": 1.3,
                "normal": 1.5,
                "relaxed": 1.7
            },
            "weights": {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            }
        }
    
    # 文本应用规则 - 调整标题的行高
    TEXT_STYLES = {
        "h1": {
            "size": "h1",
            "weight": "bold",
            "line_height": "normal"  
        },
        "h2": {
            "size": "h2",
            "weight": "semibold",
            "line_height": "normal"
        },
        "h3": {
            "size": "h3",
            "weight": "semibold",
            "line_height": "normal"
        },
        "h4": {
            "size": "h4",
            "weight": "semibold",
            "line_height": "normal"
        },
        "body": {
            "size": "body",
            "weight": "regular",
            "line_height": "normal"
        },
        "caption": {
            "size": "caption",
            "weight": "regular",
            "line_height": "normal"
        }
    }
    
    def validate(self) -> ValidationResult:
        """验证排版配置"""
        errors = []
        
        # 1. 验证基础配置
        if "ratio" not in self.TYPOGRAPHY_SYSTEM:
            errors.append("缺少排版比例配置")
        if "base_size" not in self.TYPOGRAPHY_SYSTEM:
            errors.append("缺少基础字号配置")
            
        # 2. 验证比例值
        ratio = self.TYPOGRAPHY_SYSTEM.get("ratio")
        if ratio and (ratio < 1.1 or ratio > 1.5):
            errors.append(f"排版比例 {ratio} 超出合理范围 (1.1-1.5)")
            
        # 3. 验证基础字号
        base_size = self.TYPOGRAPHY_SYSTEM.get("base_size")
        if base_size and (base_size < 12 or base_size > 16):
            errors.append(f"基础字号 {base_size}px 超出合理范围 (12-16px)")
            
        # 4. 验证字体梯度
        if "scales" not in self.TYPOGRAPHY_SYSTEM:
            errors.append("缺少字体梯度配置")
        else:
            scales = self.TYPOGRAPHY_SYSTEM["scales"]
            # 验证关键级别是否存在
            required_scales = ["caption", "body", "subtitle", "title", "h4","h3", "h2", "h1", "display"]
            for scale in required_scales:
                if scale not in scales:
                    errors.append(f"缺少必需的字体级别: {scale}")
            
            # 验证梯度递增性
            prev_value = 0
            for name, value in scales.items():
                if value <= prev_value and name not in ["caption"]:  
                    errors.append(f"字体梯度 {name} 未保持递增")
                prev_value = value
        
        # 5. 验证行高配置
        if "line_height" not in self.TYPOGRAPHY_SYSTEM:
            errors.append("缺少行高配置")
        else:
            line_heights = self.TYPOGRAPHY_SYSTEM["line_height"]
            required_line_heights = ["tight", "normal", "relaxed"]
            for lh in required_line_heights:
                if lh not in line_heights:
                    errors.append(f"缺少必需的行高配置: {lh}")
            
            for name, value in line_heights.items():
                if value < 1.0 or value > 2.0:
                    errors.append(f"行高值 {name}: {value} 超出合理范围 (1.0-2.0)")
        
        # 6. 验证字重配置
        if "weights" not in self.TYPOGRAPHY_SYSTEM:
            errors.append("缺少字重配置")
        else:
            weights = self.TYPOGRAPHY_SYSTEM["weights"]
            required_weights = ["light", "regular", "medium", "semibold", "bold"]
            for weight in required_weights:
                if weight not in weights:
                    errors.append(f"缺少必需的字重配置: {weight}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )