from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]

class BaseConfig(ABC):
    @abstractmethod
    def validate(self) -> ValidationResult:
        """验证配置"""
        pass