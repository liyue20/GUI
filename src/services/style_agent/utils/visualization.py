import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import os

class Visualizer:
    """可视化工具"""
    
    def __init__(self, save_dir: str = 'data/visualizations'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # 设置样式
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = [12, 6]
    
    def plot_training_curves(self, stats: Dict[str, List[float]], save_name: str):
        """绘制训练曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 绘制奖励曲线
        axes[0, 0].plot(stats['episode_rewards'])
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        
        # 绘制损失曲线
        axes[0, 1].plot(stats['actor_losses'], label='Actor')
        axes[0, 1].plot(stats['critic_losses'], label='Critic')
        axes[0, 1].set_title('Training Losses')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # 绘制评估分数
        axes[1, 0].plot(stats['eval_scores'])
        axes[1, 0].set_title('Evaluation Scores')
        axes[1, 0].set_xlabel('Evaluation')
        axes[1, 0].set_ylabel('Score')
        
        # 绘制最佳分数
        axes[1, 1].plot(stats['best_scores'])
        axes[1, 1].set_title('Best Scores')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Score')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.save_dir, save_name))
        plt.close()
    
    def plot_test_results(self, stats: Dict[str, List[float]], save_name: str):
        """绘制测试结果"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # 绘制分数分布
        sns.histplot(stats['scores'], ax=axes[0])
        axes[0].set_title('Test Scores Distribution')
        axes[0].set_xlabel('Score')
        axes[0].set_ylabel('Count')
        
        # 绘制步数分布
        sns.histplot(stats['steps'], ax=axes[1])
        axes[1].set_title('Steps Distribution')
        axes[1].set_xlabel('Steps')
        axes[1].set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.save_dir, save_name))
        plt.close()