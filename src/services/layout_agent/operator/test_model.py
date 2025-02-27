import sys
import os

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import torch
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from utils.layout_generator import generate_layout
from models.layout_model import DynamicPPONetwork
from src.services.layout_agent.enviroment.layout_environment import LayoutEnvironment, Block

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def plot_layout(card_width, card_height, final_positions):
    fig, ax = plt.subplots()
    ax.set_xlim(0, card_width)
    ax.set_ylim(0, card_height)
    ax.set_aspect('equal', adjustable='box')

    # 绘制卡片边界
    ax.add_patch(patches.Rectangle((0, 0), card_width, card_height, edgecolor='black', facecolor='none'))

    # 绘制每个块
    for pos in final_positions:
        x, y, width, height = pos
        rect = patches.Rectangle((x, y), width, height, edgecolor='blue', facecolor='lightblue', alpha=0.6)
        ax.add_patch(rect)

    plt.gca().invert_yaxis()  # 翻转y轴，确保原点在左上角
    plt.show()

if __name__ == "__main__":
    card_width, card_height = 1000, 800
    blocks = [
        Block(id=0, content_type='text', content_length=200, min_width=434, min_height=200),
        Block(id=1, content_type='mixed', content_length=300, min_width=300, min_height=150),
        Block(id=2, content_type='text', content_length=500, min_width=300, min_height=300),
        Block(id=3, content_type='mixed', content_length=100, min_width=200, min_height=270),
        Block(id=4, content_type='mixed', content_length=300, min_width=450, min_height=40)
    ]

    model_path = os.path.join(project_root, "data", "models", "layout", "layoutModel_05.pth")
    
    env = LayoutEnvironment(card_width, card_height, blocks)
    model = DynamicPPONetwork()
    model.load_state_dict(torch.load(model_path))
    model.float()
    
    final_positions = generate_layout(model, card_width, card_height, blocks)
    
    plot_layout(card_width, card_height, final_positions)
