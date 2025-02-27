import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def visualize_layout(card_width, card_height, blocks, positions):
    """
    可视化布局结果
    """
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, card_width)
    ax.set_ylim(0, card_height)
    ax.set_aspect('equal')

    colors = plt.cm.get_cmap('tab10')(np.linspace(0, 1, len(blocks)))
    
    for block, color in zip(blocks, colors):
        pos = positions[block.id]
        rect = patches.Rectangle(
            (pos[0], card_height - pos[1] - pos[3]), 
            pos[2], 
            pos[3],
            fill=False, 
            edgecolor=color, 
            linewidth=2
        )
        ax.add_patch(rect)
        ax.text(
            pos[0] + pos[2]/2, 
            card_height - pos[1] - pos[3]/2, 
            f'{block.content_type}\n{block.id}', 
            ha='center', 
            va='center', 
            fontsize=8, 
            color=color, 
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )

    plt.title('Card Layout')
    plt.tight_layout()
    plt.show()

def visualize_training(rewards_history, avg_rewards, best_avg_reward):
    """
    可视化训练过程
    """
    plt.figure(figsize=(12, 6))
    plt.plot(rewards_history, label='Episode Reward', alpha=0.6)
    plt.plot(avg_rewards, label='Average Reward (100 episodes)', linewidth=2)
    plt.axhline(y=best_avg_reward, color='r', linestyle='--', 
                label='Best Average Reward')
    plt.title('Training Rewards')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.legend()
    plt.show()