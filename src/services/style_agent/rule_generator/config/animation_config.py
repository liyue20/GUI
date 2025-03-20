from .base_config import BaseConfig, ValidationResult

class AnimationConfig(BaseConfig):
    """动效配置"""
    
    def __init__(self):
        """初始化动效配置"""
        super().__init__()
    
    def validate(self) -> ValidationResult:
        """验证动效配置"""
        return ValidationResult(True, []) 