from .base_generator import BaseGenerator
import random
from typing import Dict, Any, List
from ..config import AnimationConfig

class AnimationGenerator(BaseGenerator):
    """动效生成器"""
    
    def __init__(self, config: AnimationConfig = None):
        """初始化动效生成器"""
        super().__init__(config or AnimationConfig())
    
    # 预设动效库
    ANIMATIONS = {
        "entrance": [
            {
                "name": "fadeIn",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0);
                    }
                """
            },
            {
                "name": "scaleIn",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: scale(0.8);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                """
            },
            {
                "name": "slideInLeft",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: translateX(-30px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateX(0);
                    }
                """
            },
            {
                "name": "fadeInUp",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0);
                    }
                """
            },
            {
                "name": "zoomIn",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: scale(0.5);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                """
            },
            {
                "name": "slideInRight",
                "keyframes": """
                    0% {
                        opacity: 0;
                        transform: translateX(30px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateX(0);
                    }
                """
            }
        ],
        "hover": [
            {
                "name": "smoothScale",
                "keyframes": """
                    0% {
                        transform: scale(1);
                        box-shadow: 0 0 0 rgba(0, 0, 0, 0.1);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                    100% {
                        transform: scale(1.02);
                        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                """
            },
            {
                "name": "softElevate",
                "keyframes": """
                    0% {
                        transform: translateY(0);
                        box-shadow: 0 0 0 rgba(0, 0, 0, 0.1);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                    100% {
                        transform: translateY(-4px);
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                """
            },
            {
                "name": "gentleGlow",
                "keyframes": """
                    0% {
                        box-shadow: 0 0 0 rgba(var(--color-theme-primary-500-rgb), 0.1);
                        border-color: rgba(var(--color-theme-primary-500-rgb), 0.2);
                    }
                    100% {
                        box-shadow: 0 0 20px rgba(var(--color-theme-primary-500-rgb), 0.25);
                        border-color: rgba(var(--color-theme-primary-500-rgb), 0.5);
                    }
                """
            },
            {
                "name": "subtleHighlight",
                "keyframes": """
                    0% {
                        background-color: transparent;
                    }
                    100% {
                        background-color: rgba(var(--color-theme-primary-100-rgb), 0.3);
                    }
                """
            },
            {
                "name": "elegantTransform",
                "keyframes": """
                    0% {
                        transform: scale(1) translateY(0);
                        box-shadow: 0 0 0 rgba(0, 0, 0, 0.1);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                    100% {
                        transform: scale(1.02) translateY(-3px);
                        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
                        will-change: transform;
                        backface-visibility: hidden;
                        -webkit-font-smoothing: subpixel-antialiased;
                    }
                """
            },
            {
                "name": "subtleBrightness",
                "keyframes": """
                    0% {
                        filter: brightness(1) contrast(1);
                    }
                    100% {
                        filter: brightness(1.05) contrast(1.05);
                    }
                """
            }
        ],
        "emphasis": [
            {
                "name": "shake",
                "keyframes": """
                    0%, 100% {
                        transform: translateX(0);
                    }
                    25% {
                        transform: translateX(-5px);
                    }
                    75% {
                        transform: translateX(5px);
                    }
                """
            },
            {
                "name": "bounce",
                "keyframes": """
                    0%, 100% {
                        transform: translateY(0);
                    }
                    50% {
                        transform: translateY(-15px);
                    }
                """
            },
            {
                "name": "pulseFade",
                "keyframes": """
                    0% {
                        opacity: 1;
                        transform: scale(1);
                    }
                    50% {
                        opacity: 0.5;
                        transform: scale(1.05);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                """
            },
            {
                "name": "flip",
                "keyframes": """
                    0% {
                        transform: rotateY(0deg);
                    }
                    50% {
                        transform: rotateY(90deg);
                    }
                    100% {
                        transform: rotateY(0deg);
                    }
                """
            },
            {
                "name": "jelly",
                "keyframes": """
                    0% {
                        transform: scale(1);
                    }
                    30% {
                        transform: scale(1.1);
                    }
                    50% {
                        transform: scale(0.9);
                    }
                    70% {
                        transform: scale(1.05);
                    }
                    100% {
                        transform: scale(1);
                    }
                """
            },
            {
                "name": "bounceIn",
                "keyframes": """
                    0% {
                        transform: scale(0.3);
                        opacity: 0;
                    }
                    50% {
                        transform: scale(1.05);
                    }
                    100% {
                        transform: scale(1);
                        opacity: 1;
                    }
                """
            },
            {
                "name": "flash",
                "keyframes": """
                    0% {
                        opacity: 1;
                    }
                    50% {
                        opacity: 0;
                    }
                    100% {
                        opacity: 1;
                    }
                """
            }
        ]
    }

    
    def _generate_timing(self) -> Dict[str, str]:
        """生成动画时间变量"""
        return {
            "fast": "0.4s",
            "normal": "0.6s",
            "slow": "0.8s"
        }
    
    def _generate_easing(self) -> Dict[str, str]:
        """生成缓动函数变量"""
        return {
            "standard": "cubic-bezier(0.4, 0, 0.2, 1)",  # 平滑过渡
            "accelerate": "cubic-bezier(0.4, 0, 1, 1)",  # 缓慢开始
            "decelerate": "cubic-bezier(0.0, 0, 0.2, 1)", # 缓慢结束
            "smooth": "cubic-bezier(0.4, 0, 0.2, 1)"  # 平滑
        }
    
    def _select_random_animations(self) -> Dict[str, Dict]:
        """为每个元素类型随机选择动画"""
        selected = {}
        for category in self.ANIMATIONS:
            selected[category] = random.choice(self.ANIMATIONS[category])
        return selected
    
    def generate(self, layout_info: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成动效规则"""
        try:
            timing = self._generate_timing()
            easing = self._generate_easing()
            animations = self._select_random_animations()
            
            return {
                "timing": timing,
                "easing": easing,
                "animations": animations
            }
            
        except Exception as e:
            raise RuntimeError(f"生成动效规则失败: {str(e)}") 