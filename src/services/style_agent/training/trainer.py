from typing import Dict, List
import torch
import numpy as np
from tqdm import tqdm
import logging

class StyleTrainer:
    """样式训练器"""
    
    def __init__(self, model, environment, save_path: str = 'models/style_model.pth'):
        self.model = model
        self.env = environment
        self.save_path = save_path
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def train(self, layout_infos: Dict, episodes: int = 1000, 
             eval_interval: int = 50) -> Dict:
        """训练模型"""
        training_history = {
            'episode_rewards': [],
            'eval_scores': []
        }
        
        best_eval_score = float('-inf')
        
        for episode in tqdm(range(episodes)):
            # 训练一个episode
            episode_reward = self._train_episode(layout_infos)
            training_history['episode_rewards'].append(episode_reward)
            
            # 定期评估
            if (episode + 1) % eval_interval == 0:
                eval_score = self._evaluate(layout_infos)
                training_history['eval_scores'].append(eval_score)
                
                self.logger.info(
                    f"Episode {episode+1}/{episodes} - "
                    f"Evaluation Score: {eval_score:.3f}"
                )
                
                # 保存最佳模型
                if eval_score > best_eval_score:
                    best_eval_score = eval_score
                    self.model.save(self.save_path)
        
        return training_history
    
    def _train_episode(self, layout_infos: Dict) -> float:
        """训练单个episode"""
        state = self.env.reset(layout_infos)
        total_reward = 0
        done = False
        
        while not done:
            # 选择动作
            action = self.model.choose_action(state, training=True)
            
            # 执行动作
            next_state, reward, done, _ = self.env.step(action)
            
            # 存储经验
            self.model.remember(state, action, reward, next_state, done)
            
            # 训练模型
            loss = self.model.replay()
            
            total_reward += reward
            state = next_state
        
        return total_reward
    
    def _evaluate(self, layout_infos: Dict, n_episodes: int = 5) -> float:
        """评估模型"""
        eval_scores = []
        
        for _ in range(n_episodes):
            state = self.env.reset(layout_infos)
            done = False
            episode_score = 0
            
            while not done:
                # 选择动作（不使用探索）
                action = self.model.choose_action(state, training=False)
                
                # 执行动作
                next_state, reward, done, _ = self.env.step(action)
                
                episode_score += reward
                state = next_state
            
            eval_scores.append(episode_score)
        
        return np.mean(eval_scores)