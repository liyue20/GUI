import os
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np
import random
from tqdm import tqdm
from src.utils.logging import logging
from torch.utils.tensorboard import SummaryWriter

logger = logging.getLogger('project_logger')

def compute_returns_and_advantages(trajectory, discount_factor=0.99, gae_lambda=0.95):
    """计算回报（returns）和优势（advantages）。"""
    returns = []
    advantages = []
    R = 0
    advantage = 0
    # 从最后一步开始逆序计算
    for t in reversed(range(len(trajectory))):
        R = trajectory[t]['reward'] + discount_factor * R * (1 - trajectory[t]['done'])
        returns.insert(0, R)
        # 计算TD误差
        if t < len(trajectory) - 1:
            td_error = trajectory[t]['reward'] + discount_factor * trajectory[t+1]['value'] * (1 - trajectory[t]['done']) - trajectory[t]['value']
        else:
            # 最后一步无下一个状态值，TD误差视为0
            td_error = 0
        advantage = td_error + discount_factor * gae_lambda * advantage * (1 - trajectory[t]['done'])
        advantages.insert(0, advantage)
    # 转为张量并标准化优势
    returns = torch.tensor(returns, dtype=torch.float32)
    advantages = torch.tensor(advantages, dtype=torch.float32)
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    return returns, advantages

def ppo_update(model, optimizer, trajectories, returns, advantages, ppo_clip_value, value_loss_coef, entropy_coef, max_grad_norm, ppo_epochs=10, batch_size=32, device=torch.device('cpu'), temperature=1.0):
    """使用 PPO 算法更新策略网络参数。"""
    model.train()
    last_actor_loss = None
    last_critic_loss = None
    last_total_loss = None
    # 多轮次PPO迭代
    for _ in range(ppo_epochs):
        indices = np.arange(len(trajectories))
        np.random.shuffle(indices)
        # 按批次大小进行更新
        for start in range(0, len(trajectories), batch_size):
            end = start + batch_size
            batch_idx = indices[start:end]
            if len(batch_idx) < 2:
                continue  # 略过样本过少的小批次
            # 准备当前批次的数据张量
            batch_states = torch.FloatTensor([trajectories[i]['state'] for i in batch_idx]).to(device)
            batch_block_actions = torch.tensor([trajectories[i]['block_selection'] for i in batch_idx]).to(device)
            batch_action_actions = torch.tensor([trajectories[i]['action_selection'] for i in batch_idx]).to(device)
            batch_old_log_probs = torch.tensor([trajectories[i]['log_prob'] for i in batch_idx]).to(device)
            batch_returns = returns[batch_idx].to(device)
            batch_advantages = advantages[batch_idx].to(device)
            # 前向传播计算当前策略的输出
            block_logits, action_logits, state_values = model(batch_states)
            # 计算策略的概率分布（加入极小值避免log(0)）
            block_probs = F.softmax(block_logits / temperature, dim=-1) + 1e-8
            action_probs = F.softmax(action_logits / temperature, dim=-1) + 1e-8
            block_dist = torch.distributions.Categorical(probs=block_probs)
            action_dist = torch.distributions.Categorical(probs=action_probs)
            # 计算新策略下选定动作的对数概率
            new_log_probs = block_dist.log_prob(batch_block_actions) + action_dist.log_prob(batch_action_actions)
            # 计算 PPO 损失各项
            ratio = torch.exp(new_log_probs - batch_old_log_probs)
            surr1 = ratio * batch_advantages
            surr2 = torch.clamp(ratio, 1.0 - ppo_clip_value, 1.0 + ppo_clip_value) * batch_advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = F.mse_loss(state_values.squeeze(-1), batch_returns)
            entropy = block_dist.entropy().mean() + action_dist.entropy().mean()
            loss = actor_loss + value_loss_coef * critic_loss - entropy_coef * entropy
            # 反向传播并更新参数
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            optimizer.step()
            # 记录最后一次更新的损失值
            last_actor_loss = actor_loss.item()
            last_critic_loss = critic_loss.item()
            last_total_loss = loss.item()
    return last_actor_loss, last_critic_loss, last_total_loss
def train(env, model, optimizer, num_episodes=10, max_steps_per_episode=10, num_envs=4, log_interval=10):
    # 设置TensorBoard记录器和日志目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    writer = SummaryWriter(log_dir)
    # 输出GPU信息
    print(torch.cuda.is_available())         # 检查GPU可用性
    print(torch.cuda.current_device())       # 当前使用的GPU序号
    if torch.cuda.is_available():
        print(torch.cuda.get_device_name(torch.cuda.current_device()))  # 当前GPU名称
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.float()
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20, verbose=True)
    
    # 创建多环境实例用于并行采样
    envs = [env]
    for i in range(1, num_envs):
        envs.append(env.__class__(env.card_width, env.card_height, env.blocks))
    
    rewards_history = []
    avg_rewards = []
    best_avg_reward = float('-inf')
    best_model_state = None
    
    # PPO算法相关参数初始化
    ppo_clip_value = 0.2
    value_loss_coef = 0.5
    initial_entropy_coef = 0.01
    final_entropy_coef = 0.0
    max_grad_norm = 0.5
    ppo_epochs = 10
    discount_factor = 0.99
    gae_lambda = 0.95
    initial_epsilon = 0.1
    initial_temperature = 1.0
    
    episodes_completed = 0  # 已完成的episode计数
    # 主训练循环
    while episodes_completed < num_episodes:
        # 确定本轮并行的环境数量
        active_envs = min(num_envs, num_episodes - episodes_completed)
        states = []
        episode_rewards = [0.0] * active_envs
        episode_data = [[] for _ in range(active_envs)]
        done_flags = [False] * active_envs
        # 重置各环境并获取初始状态和奖励
        for i in range(active_envs):
            s, initial_reward = envs[i].reset()
            states.append(s)
            episode_rewards[i] = initial_reward
        # 计算本批episode的初始探索参数
        epsilon = max(0.01, initial_epsilon * (1 - episodes_completed / num_episodes))
        temperature = max(0.5, initial_temperature * (1 - episodes_completed / num_episodes))
        # 同步执行多个环境的交互步骤
        for step in range(max_steps_per_episode):
            state_tensor = torch.FloatTensor(np.array(states)).to(device)
            with torch.no_grad():
                block_logits, action_logits, state_values = model(state_tensor)
            # 基于模型输出构建策略分布
            block_dist_full = torch.distributions.Categorical(logits=block_logits)
            action_dist_full = torch.distributions.Categorical(logits=action_logits)
            block_dist_temp = torch.distributions.Categorical(logits=block_logits / temperature)
            action_dist_temp = torch.distributions.Categorical(logits=action_logits / temperature)
            # 为每个环境选择动作
            block_actions = block_dist_temp.sample()   # Tensor大小: [active_envs]
            action_actions = action_dist_temp.sample()
            for i in range(active_envs):
                if done_flags[i]:
                    continue  # 跳过已完成的环境
                # Epsilon-greedy 探索：以 epsilon 概率随机选动作
                if random.random() < epsilon:
                    block_count = len(envs[i].blocks)
                    block_actions[i] = random.randint(0, block_count - 1)
                    action_actions[i] = random.randint(0, 7)
                # 计算选定动作在当前策略下的对数概率
                log_prob = (block_dist_full.log_prob(block_actions).sum(dim=-1) + 
                            action_dist_full.log_prob(action_actions).sum(dim=-1))
                # 环境执行该动作
                next_state, reward, done, info = envs[i].step(int(block_actions[i].item()), int(action_actions[i].item()))
                # 保存经验数据
                episode_data[i].append({
                    'state': states[i],
                    'block_selection': int(block_actions[i].item()),
                    'action_selection': int(action_actions[i].item()),
                    'log_prob': log_prob.item(),  # 直接使用 item() 获取标量
                    'value': state_values[i].item(),
                    'reward': reward,
                    'done': done,
                    'info': info
                })
                states[i] = next_state
                episode_rewards[i] += reward
                done_flags[i] = done or (step == max_steps_per_episode - 1)
                if done_flags[i]:
                    # 当前环境一个episode结束
                    episodes_completed += 1
                    rewards_history.append(episode_rewards[i])
                    avg_reward = np.mean(rewards_history[-100:])
                    avg_rewards.append(avg_reward)
                    if avg_reward > best_avg_reward:
                        best_avg_reward = avg_reward
                        best_model_state = model.state_dict()
                        # 保存当前最佳模型参数
                        os.makedirs(os.path.join(project_root, "checkpoints"), exist_ok=True)
                        torch.save(best_model_state, os.path.join(project_root, "checkpoints", "best_model.pth"))
                    # 按设置的日志间隔记录训练日志
                    if episodes_completed % log_interval == 0 or episodes_completed == num_episodes:
                        logger.info(f"Episode {episodes_completed}, Reward: {episode_rewards[i]:.2f}, Steps: {len(episode_data[i])}, Epsilon: {epsilon:.3f}, Temperature: {temperature:.3f}")
                        print(f"Episode {episodes_completed}, Avg Reward: {avg_reward:.2f}, Best Avg Reward: {best_avg_reward:.2f}, PPO Clip: {ppo_clip_value:.3f}")
                        print("Reward Breakdown:", episode_data[i][-1]['info'])
            if all(done_flags[:active_envs]):
                # 所有环境都完成当前episode
                break
        # 如果有episode因为达到最大步数而截断，标记done以正确计算优势
        for i in range(active_envs):
            if episode_data[i] and episode_data[i][-1]['done'] is False:
                episode_data[i][-1]['done'] = True
        # 汇总所有环境收集的轨迹数据
        all_trajectories = []
        for i in range(active_envs):
            all_trajectories.extend(episode_data[i])
        if len(all_trajectories) == 0:
            continue
        # 计算回报和优势（使用GAE）
        returns, advantages = compute_returns_and_advantages(all_trajectories, discount_factor, gae_lambda)
        returns = returns.to(device)
        advantages = advantages.to(device)
        # 动态调整熵系数：随训练逐步降低探索强度
        entropy_coef = final_entropy_coef + (initial_entropy_coef - final_entropy_coef) * max(0, 1 - episodes_completed / num_episodes)
        # 执行 PPO 更新策略网络
        actor_loss, critic_loss, total_loss = ppo_update(model, optimizer, all_trajectories, returns, advantages, ppo_clip_value, value_loss_coef, entropy_coef, max_grad_norm, ppo_epochs, batch_size=32, device=device, temperature=temperature)
        # 更新学习率调度器（根据最近平均奖励）
        scheduler.step(avg_reward)
        # 缓慢缩小 PPO 剪切范围，提高训练稳定性
        ppo_clip_value = max(0.1, ppo_clip_value * 0.995)
        # 按日志间隔记录损失值到 TensorBoard
        if episodes_completed % log_interval == 0 or episodes_completed == num_episodes:
            if actor_loss is not None and critic_loss is not None:
                writer.add_scalar('Loss/Actor', actor_loss, episodes_completed)
                writer.add_scalar('Loss/Critic', critic_loss, episodes_completed)
                writer.add_scalar('Loss/Total', total_loss, episodes_completed)
            writer.add_scalar('Reward/Avg100', avg_reward, episodes_completed)
    writer.close()
    return model, rewards_history, avg_rewards, best_model_state, best_avg_reward


def train_old(env, model, optimizer, num_episodes=300, max_steps_per_episode=700, num_envs=4, log_interval=10):
    # 设置TensorBoard记录器和日志目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    writer = SummaryWriter(log_dir)
    # 确保优化器使用权重衰减（如未设置则添加）
    for param_group in optimizer.param_groups:
        if 'weight_decay' not in param_group or param_group['weight_decay'] == 0:
            param_group['weight_decay'] = 1e-4  # 添加适度权重衰减
    
    # 输出GPU信息
    print(torch.cuda.is_available())         # 检查GPU可用性
    print(torch.cuda.current_device())       # 当前使用的GPU序号
    if torch.cuda.is_available():
        print(torch.cuda.get_device_name(torch.cuda.current_device()))  # 当前GPU名称
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.float()
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20, verbose=True)
    
    # 创建多环境实例用于并行采样
    envs = [env]
    for i in range(1, num_envs):
        envs.append(env.__class__(env.card_width, env.card_height, env.blocks))
    
    rewards_history = []
    avg_rewards = []
    best_avg_reward = float('-inf')
    best_model_state = None
    
    # PPO算法相关参数初始化
    ppo_clip_value = 0.2
    value_loss_coef = 0.5
    initial_entropy_coef = 0.01
    final_entropy_coef = 0.0
    max_grad_norm = 0.5
    ppo_epochs = 10
    discount_factor = 0.99
    gae_lambda = 0.95
    initial_epsilon = 0.1
    initial_temperature = 1.0
    
    episodes_completed = 0  # 已完成的episode计数
    # 主训练循环
    while episodes_completed < num_episodes:
        # 确定本轮并行的环境数量
        active_envs = min(num_envs, num_episodes - episodes_completed)
        states = []
        episode_rewards = [0.0] * active_envs
        episode_data = [[] for _ in range(active_envs)]
        done_flags = [False] * active_envs
        # 重置各环境并获取初始状态和奖励
        for i in range(active_envs):
            s, initial_reward = envs[i].reset()
            states.append(s)
            episode_rewards[i] = initial_reward
        # 计算本批episode的初始探索参数
        epsilon = max(0.01, initial_epsilon * (1 - episodes_completed / num_episodes))
        temperature = max(0.5, initial_temperature * (1 - episodes_completed / num_episodes))
        # 同步执行多个环境的交互步骤
        for step in range(max_steps_per_episode):
            state_tensor = torch.FloatTensor(np.array(states)).to(device)
            with torch.no_grad():
                block_logits, action_logits, state_values = model(state_tensor)
            # 基于模型输出构建策略分布
            block_dist_full = torch.distributions.Categorical(logits=block_logits)
            action_dist_full = torch.distributions.Categorical(logits=action_logits)
            block_dist_temp = torch.distributions.Categorical(logits=block_logits / temperature)
            action_dist_temp = torch.distributions.Categorical(logits=action_logits / temperature)
            # 为每个环境选择动作
            block_actions = block_dist_temp.sample()   # Tensor大小: [active_envs]
            action_actions = action_dist_temp.sample()
            for i in range(active_envs):
                if done_flags[i]:
                    continue  # 跳过已完成的环境
                # Epsilon-greedy 探索：以 epsilon 概率随机选动作
                if random.random() < epsilon:
                    block_count = len(envs[i].blocks)
                    block_actions[i] = random.randint(0, block_count - 1)
                    action_actions[i] = random.randint(0, 7)
                # 计算选定动作在当前策略下的对数概率
                log_prob = (block_dist_full.log_prob(block_actions[i]) + action_dist_full.log_prob(action_actions[i])).item()
                # 环境执行该动作
                next_state, reward, done, info = envs[i].step(int(block_actions[i].item()), int(action_actions[i].item()))
                # 保存经验数据
                episode_data[i].append({
                    'state': states[i],
                    'block_selection': int(block_actions[i].item()),
                    'action_selection': int(action_actions[i].item()),
                    'log_prob': log_prob,
                    'value': state_values[i].item(),
                    'reward': reward,
                    'done': done,
                    'info': info
                })
                states[i] = next_state
                episode_rewards[i] += reward
                done_flags[i] = done or (step == max_steps_per_episode - 1)
                if done_flags[i]:
                    # 当前环境一个episode结束
                    episodes_completed += 1
                    rewards_history.append(episode_rewards[i])
                    avg_reward = np.mean(rewards_history[-100:])
                    avg_rewards.append(avg_reward)
                    if avg_reward > best_avg_reward:
                        best_avg_reward = avg_reward
                        best_model_state = model.state_dict()
                        # 保存当前最佳模型参数
                        os.makedirs(os.path.join(project_root, "checkpoints"), exist_ok=True)
                        torch.save(best_model_state, os.path.join(project_root, "checkpoints", "best_model.pth"))
                    # 按设置的日志间隔记录训练日志
                    if episodes_completed % log_interval == 0 or episodes_completed == num_episodes:
                        logger.info(f"Episode {episodes_completed}, Reward: {episode_rewards[i]:.2f}, Steps: {len(episode_data[i])}, Epsilon: {epsilon:.3f}, Temperature: {temperature:.3f}")
                        print(f"Episode {episodes_completed}, Avg Reward: {avg_reward:.2f}, Best Avg Reward: {best_avg_reward:.2f}, PPO Clip: {ppo_clip_value:.3f}")
                        print("Reward Breakdown:", episode_data[i][-1]['info'])
            if all(done_flags[:active_envs]):
                # 所有环境都完成当前episode
                break
        # 如果有episode因为达到最大步数而截断，标记done以正确计算优势
        for i in range(active_envs):
            if episode_data[i] and episode_data[i][-1]['done'] is False:
                episode_data[i][-1]['done'] = True
        # 汇总所有环境收集的轨迹数据
        all_trajectories = []
        for i in range(active_envs):
            all_trajectories.extend(episode_data[i])
        if len(all_trajectories) == 0:
            continue
        # 计算回报和优势（使用GAE）
        returns, advantages = compute_returns_and_advantages(all_trajectories, discount_factor, gae_lambda)
        returns = returns.to(device)
        advantages = advantages.to(device)
        # 动态调整熵系数：随训练逐步降低探索强度
        entropy_coef = final_entropy_coef + (initial_entropy_coef - final_entropy_coef) * max(0, 1 - episodes_completed / num_episodes)
        # 执行 PPO 更新策略网络
        actor_loss, critic_loss, total_loss = ppo_update(model, optimizer, all_trajectories, returns, advantages, ppo_clip_value, value_loss_coef, entropy_coef, max_grad_norm, ppo_epochs, batch_size=32, device=device, temperature=temperature)
        # 更新学习率调度器（根据最近平均奖励）
        scheduler.step(avg_reward)
        # 缓慢缩小 PPO 剪切范围，提高训练稳定性
        ppo_clip_value = max(0.1, ppo_clip_value * 0.995)
        # 按日志间隔记录损失值到 TensorBoard
        if episodes_completed % log_interval == 0 or episodes_completed == num_episodes:
            if actor_loss is not None and critic_loss is not None:
                writer.add_scalar('Loss/Actor', actor_loss, episodes_completed)
                writer.add_scalar('Loss/Critic', critic_loss, episodes_completed)
                writer.add_scalar('Loss/Total', total_loss, episodes_completed)
            writer.add_scalar('Reward/Avg100', avg_reward, episodes_completed)
    writer.close()
    return model, rewards_history, avg_rewards, best_model_state, best_avg_reward
