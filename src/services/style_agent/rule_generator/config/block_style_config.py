from .base_config import BaseConfig, ValidationResult

class BlockStyleConfig(BaseConfig):
    """块样式配置"""
    
    def __init__(self, style_preset=None):
        """初始化块样式配置"""
        super().__init__()
        self.style_preset = style_preset or "advanced"
    
    def validate(self) -> ValidationResult:
        """验证块样式配置"""
        errors = []
        
        # 验证样式预设是否有效
        valid_presets = ["simple", "advanced", "modern", "classic", "playful"]
        if self.style_preset not in valid_presets:
            errors.append(f"无效的样式预设: {self.style_preset}，有效值为: {', '.join(valid_presets)}")
        
        return ValidationResult(len(errors) == 0, errors) 