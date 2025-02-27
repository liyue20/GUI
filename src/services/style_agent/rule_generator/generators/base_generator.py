from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseGenerator(ABC):
    """生成器基类"""
    
    def __init__(self, config: Any):
        self.config = config
    
    @abstractmethod
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成规则"""
        pass
