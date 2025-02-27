import sys
import os

# 将项目根目录添加到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
os.chdir(project_root)
sys.path.append(project_root)


import torch
import torch.optim as optim
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

    trained_model, rewards_history, avg_rewards, best_model_state, best_avg_reward = train(env, model, optimizer, num_episodes=64)
    
    torch.save(best_model_state, os.path.join(project_root, "data", "save_model", "layout", "layoutModel_06.pth"))