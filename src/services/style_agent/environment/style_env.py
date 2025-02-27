from typing import Dict, Tuple, Any
import numpy as np
from .action_space import ActionSpace

class StyleEnvironment:
    """样式环境"""
    
    def __init__(self, rule_generator, runtime_manager):
        self.rule_generator = rule_generator
        self.runtime = runtime_manager
        self.action_space = ActionSpace()
        
        # 环境状态
        self.current_layout = None
        self.current_style = None
        self.current_score = None
        self.history_scores = []
        
        # 环境参数
        self.max_steps = 20
        self.current_step = 0
        
    def reset(self, layout_infos: Dict) -> Dict:
        """
        重置环境
        
        Args:
            layout_infos: 布局信息
            
        Returns:
            Dict: 初始状态
        """
        self.current_layout = layout_infos
        self.current_style = self.rule_generator.generate_style()
        self.current_score = self.runtime.evaluate_design(
            layout_infos, 
            self.current_style
        )
        
        self.history_scores = [self.current_score]
        self.current_step = 0
        
        return self._get_state()
    
    def step(self, action: int) -> Tuple[Dict, float, bool, Dict]:
        """
        执行一步
        
        Args:
            action: 动作索引
            
        Returns:
            Tuple[Dict, float, bool, Dict]: (新状态, 奖励, 是否结束, 信息)
        """
        self.current_step += 1
        
        # 获取动作名称
        action_name = self.action_space.get_action(action)
        
        # 应用动作
        new_style = self.action_space.apply_action(
            action_name, 
            self.current_style
        )
        
        # 评估新样式
        new_score = self.runtime.evaluate_design(
            self.current_layout, 
            new_style
        )
        
        # 计算奖励
        reward = self._calculate_reward(new_score)
        
        # 更新状态
        self.current_style = new_style
        self.current_score = new_score
        self.history_scores.append(new_score)
        
        # 检查是否结束
        done = self._is_done()
        
        # 附加信息
        info = {
            'step': self.current_step,
            'action': action_name,
            'score_improvement': new_score - self.history_scores[0]
        }
        
        return self._get_state(), reward, done, info
    
    def _get_state(self) -> Dict:
        """获取当前状态"""
        return {
            'style': self.current_style,
            'score': self.current_score,
            'history_scores': self.history_scores[-5:],  # 最近5个分数
            'step': self.current_step
        }
    
    def _calculate_reward(self, new_score: float) -> float:
        """计算奖励"""
        # 基础奖励：分数提升
        reward = new_score - self.current_score
        
        # 额外奖励：如果超过历史最佳
        if new_score > max(self.history_scores):
            reward += 0.5
        
        # 惩罚：如果分数显著下降
        if reward < -0.1:
            reward *= 1.5
        
        return reward
    
    def _is_done(self) -> bool:
        """检查是否结束"""
        # 达到最大步数
        if self.current_step >= self.max_steps:
            return True
        
        # 连续3步没有改善
        if len(self.history_scores) >= 3:
            recent_scores = self.history_scores[-3:]
            if all(x <= recent_scores[0] for x in recent_scores):
                return True
        
        return False