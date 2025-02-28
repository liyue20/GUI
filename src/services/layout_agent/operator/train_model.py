import sys
import os
import torch
import torch.optim as optim

# 将项目根目录添加到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
os.chdir(project_root)
sys.path.append(project_root)

from src.services.layout_agent.models.layout_model import DynamicPPONetwork
from src.services.layout_agent.enviroment.layout_environment import LayoutEnvironment, Block
from src.services.layout_agent.training.train import train
from src.utils.logging import setup_logger

if __name__ == "__main__":
    logger = setup_logger()
    logger.info("主程序启动")

    card_width, card_height = 1020, 1195
    blocks = [
        Block(id=0, content_type='text', content_length=107, min_width=316, min_height=215),
        Block(id=1, content_type='text', content_length=133, min_width=422, min_height=215),
        Block(id=2, content_type='text', content_length=195, min_width=510, min_height=238),
        Block(id=3, content_type='mixed', content_length=313, min_width=316, min_height=428)
    ]

    env = LayoutEnvironment(card_width, card_height, blocks)
    model = DynamicPPONetwork()
    model.float()
    optimizer = optim.Adam(model.parameters(), lr=0.0003)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.7)

    # 目标路径
    save_path = os.path.join(project_root, "data", "models", "layout")
    os.makedirs(save_path, exist_ok=True)

    best_avg_reward = -float('inf')

    # 训练模型
    for episode in range(128):
        trained_model, rewards_history, avg_rewards, model_state, avg_reward = train(env, model, optimizer, num_episodes=64)
        
        if avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            checkpoint_path = os.path.join(save_path, f"best_layout_model.pth")
            torch.save(model_state, checkpoint_path)
            logger.info(f"Best model saved: {checkpoint_path}")

        if episode % 10 == 0:
            save_file = os.path.join(save_path, f"layoutModel_{episode}_{avg_reward:.2f}.pth")
            torch.save(model_state, save_file)
            logger.info(f"Episode {episode} 模型已保存: {save_file}")
        
        # 更新学习率
        scheduler.step()

