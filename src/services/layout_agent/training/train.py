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

def select_action(network, state, epsilon=0.1, temperature=1.0):
    if random.random() < epsilon:
        block_selection = random.randint(0, state.shape[1] - 1)
        action_selection = random.randint(0, 7)
        return block_selection, action_selection

    with torch.no_grad():
        block_logits, action_logits, _ = network(state)
        block_probs = F.softmax(block_logits / temperature, dim=-1)
        action_probs = F.softmax(action_logits / temperature, dim=-1)
    
    block_selection = torch.multinomial(block_probs[0], 1).item()
    action_selection = torch.multinomial(action_probs[0], 1).item()

    return block_selection, action_selection

def train_old(env, model, optimizer, num_episodes=300, max_steps_per_episode=700):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.float()

    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20, verbose=True)

    rewards_history = []
    avg_rewards = []
    best_avg_reward = float('-inf')
    best_model_state = None

    ppo_clip_value = 0.2
    value_loss_coef = 0.5
    entropy_coef = 0.01
    max_grad_norm = 0.5
    ppo_epochs = 10
    discount_factor = 0.99
    gae_lambda = 0.95

    initial_epsilon = 0.1
    initial_temperature = 1.0

    for episode in tqdm(range(num_episodes), desc="Training Progress"):
        epsilon = max(0.01, initial_epsilon * (1 - episode / num_episodes))
        temperature = max(0.5, initial_temperature * (1 - episode / num_episodes))

        state, initial_reward = env.reset()
        episode_reward = initial_reward
        episode_data = []
        
        for step in range(max_steps_per_episode):
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
            block_selection, action_selection = select_action(model, state_tensor, epsilon, temperature)

            with torch.no_grad():
                block_logits, action_logits, state_value = model(state_tensor)
            
            block_dist = torch.distributions.Categorical(logits=block_logits)
            action_dist = torch.distributions.Categorical(logits=action_logits)
            
            log_prob = block_dist.log_prob(torch.tensor(block_selection).to(device)) + \
                       action_dist.log_prob(torch.tensor(action_selection).to(device))
            
            next_state, reward, done, info = env.step(block_selection, action_selection)
            episode_data.append({
                'state': state,
                'block_selection': block_selection,
                'action_selection': action_selection,
                'log_prob': log_prob.item(),
                'value': state_value.item(),
                'reward': reward,
                'done': done,
                'info': info
            })
            
            state = next_state
            episode_reward += reward
            
            if done and step > 32:
                break
        
        logger.info(f"Episode {episode}, Reward: {episode_reward:.2f}, Steps: {len(episode_data)}, Epsilon: {epsilon:.3f}, Temperature: {temperature:.3f}")

        rewards_history.append(episode_reward)
        avg_reward = np.mean(rewards_history[-100:])
        avg_rewards.append(avg_reward)
        
        if avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            best_model_state = model.state_dict()

        returns = []
        advantages = []
        R = 0
        advantage = 0
        for t in reversed(range(len(episode_data))):
            R = episode_data[t]['reward'] + discount_factor * R * (1 - episode_data[t]['done'])
            returns.insert(0, R)
            
            td_error = episode_data[t]['reward'] + discount_factor * episode_data[t+1]['value'] * (1 - episode_data[t]['done']) - episode_data[t]['value'] if t < len(episode_data) - 1 else 0
            advantage = td_error + discount_factor * gae_lambda * advantage * (1 - episode_data[t]['done'])
            advantages.insert(0, advantage)
        
        returns = torch.tensor(returns, dtype=torch.float32).to(device)
        advantages = torch.tensor(advantages, dtype=torch.float32).to(device)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        for _ in range(ppo_epochs):
            for i in range(0, len(episode_data), 32):
                batch = episode_data[i:i+32]
                # print("---batch length-----",len(batch))
                if len(batch) < 2:
                    continue  # 跳过太小的批次
                states = torch.FloatTensor([item['state'] for item in batch]).to(device)
                block_selections = torch.tensor([item['block_selection'] for item in batch]).to(device)
                action_selections = torch.tensor([item['action_selection'] for item in batch]).to(device)
                old_log_probs = torch.tensor([item['log_prob'] for item in batch]).to(device)
                batch_returns = returns[i:i+32]
                batch_advantages = advantages[i:i+32]
                
                block_logits, action_logits, state_values = model(states)

                block_probs = F.softmax(block_logits / temperature, dim=-1) + 1e-8
                action_probs = F.softmax(action_logits / temperature, dim=-1) + 1e-8

                block_dist = torch.distributions.Categorical(probs=block_probs)
                action_dist = torch.distributions.Categorical(probs=action_probs)
                
                new_log_probs = block_dist.log_prob(block_selections) + action_dist.log_prob(action_selections)
                
                ratio = (new_log_probs - old_log_probs).exp()
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1.0 - ppo_clip_value, 1.0 + ppo_clip_value) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()
                critic_loss = F.mse_loss(state_values.squeeze(), batch_returns)
                entropy = block_dist.entropy().mean() + action_dist.entropy().mean()
                
                loss = actor_loss + value_loss_coef * critic_loss - entropy_coef * entropy
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
                optimizer.step()
        
        scheduler.step(avg_reward)
        
        ppo_clip_value = max(0.1, ppo_clip_value * 0.999)

        #if episode % 10 == 0:
        print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, Best Avg Reward: {best_avg_reward:.2f}, PPO Clip: {ppo_clip_value:.3f}")
        print("Reward Breakdown:", episode_data[-1]['info'])

    return model, rewards_history, avg_rewards, best_model_state, best_avg_reward

def train(env, model, optimizer, num_episodes=300, max_steps_per_episode=1000):
    # 初始化 TensorBoard 写入器
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    writer = SummaryWriter(os.path.join(project_root, "logs"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.float()
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20)
    rewards_history = []
    avg_rewards = []
    best_avg_reward = float('-inf')
    best_model_state = None
    ppo_clip_value = 0.2
    value_loss_coef = 0.5
    entropy_coef = 0.01
    max_grad_norm = 0.5
    ppo_epochs = 10
    discount_factor = 0.99
    gae_lambda = 0.95
    initial_epsilon = 0.1
    initial_temperature = 1.0
    for episode in tqdm(range(num_episodes), desc="Training Progress"):
        epsilon = max(0.01, initial_epsilon * (1 - episode / num_episodes))
        temperature = max(0.5, initial_temperature * (1 - episode / num_episodes))
        state, initial_reward = env.reset()
        episode_reward = initial_reward
        episode_data = []
        for step in range(max_steps_per_episode):
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
            block_selection, action_selection = select_action(model, state_tensor, epsilon, temperature)
            with torch.no_grad():
                block_logits, action_logits, state_value = model(state_tensor)
            block_dist = torch.distributions.Categorical(logits=block_logits)
            action_dist = torch.distributions.Categorical(logits=action_logits)
            log_prob = block_dist.log_prob(torch.tensor(block_selection).to(device)) + \
                       action_dist.log_prob(torch.tensor(action_selection).to(device))
            next_state, reward, done, info = env.step(block_selection, action_selection)
            episode_data.append({
                'state': state,
                'block_selection': block_selection,
                'action_selection': action_selection,
                'log_prob': log_prob.item(),
                'value': state_value.item(),
                'reward': reward,
                'done': done,
                'info': info
            })
            state = next_state
            episode_reward += reward
            if done and step > 32:
                break
            
        logger.info(f"Episode {episode}, Reward: {episode_reward:.2f}, Steps: {len(episode_data)}, Epsilon: {epsilon:.3f}, Temperature: {temperature:.3f}")
        rewards_history.append(episode_reward)
        avg_reward = np.mean(rewards_history[-100:])
        avg_rewards.append(avg_reward)
        # Log rewards and loss to TensorBoard
        writer.add_scalar('Reward/Episode Reward', episode_reward, episode)
        writer.add_scalar('Reward/Avg Reward (last 100)', avg_reward, episode)
        if avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            best_model_state = model.state_dict()
        returns = []
        advantages = []
        R = 0
        advantage = 0
        for t in reversed(range(len(episode_data))):
            R = episode_data[t]['reward'] + discount_factor * R * (1 - episode_data[t]['done'])
            returns.insert(0, R)
            td_error = episode_data[t]['reward'] + discount_factor * episode_data[t+1]['value'] * (1 - episode_data[t]['done']) - episode_data[t]['value'] if t < len(episode_data) - 1 else 0
            advantage = td_error + discount_factor * gae_lambda * advantage * (1 - episode_data[t]['done'])
            advantages.insert(0, advantage)
        returns = torch.tensor(returns, dtype=torch.float32).to(device)
        advantages = torch.tensor(advantages, dtype=torch.float32).to(device)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        for _ in range(ppo_epochs):
            for i in range(0, len(episode_data), 32):
                batch = episode_data[i:i+32]
                if len(batch) < 2:
                    continue  # 跳过太小的批次
                states = torch.FloatTensor([item['state'] for item in batch]).to(device)
                block_selections = torch.tensor([item['block_selection'] for item in batch]).to(device)
                action_selections = torch.tensor([item['action_selection'] for item in batch]).to(device)
                old_log_probs = torch.tensor([item['log_prob'] for item in batch]).to(device)
                batch_returns = returns[i:i+32]
                batch_advantages = advantages[i:i+32]
                block_logits, action_logits, state_values = model(states)
                block_probs = F.softmax(block_logits / temperature, dim=-1) + 1e-8
                action_probs = F.softmax(action_logits / temperature, dim=-1) + 1e-8
                block_dist = torch.distributions.Categorical(probs=block_probs)
                action_dist = torch.distributions.Categorical(probs=action_probs)
                new_log_probs = block_dist.log_prob(block_selections) + action_dist.log_prob(action_selections)
                ratio = (new_log_probs - old_log_probs).exp()
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1.0 - ppo_clip_value, 1.0 + ppo_clip_value) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()
                critic_loss = F.mse_loss(state_values.squeeze(), batch_returns)
                entropy = block_dist.entropy().mean() + action_dist.entropy().mean()
                loss = actor_loss + value_loss_coef * critic_loss - entropy_coef * entropy
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
                optimizer.step()
        scheduler.step(avg_reward)
        ppo_clip_value = max(0.1, ppo_clip_value * 0.999)
        # Log loss to TensorBoard
        writer.add_scalar('Loss/Actor Loss', actor_loss.item(), episode)
        writer.add_scalar('Loss/Critic Loss', critic_loss.item(), episode)
        writer.add_scalar('Loss/Total Loss', loss.item(), episode)
        
        print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, Best Avg Reward: {best_avg_reward:.2f}, PPO Clip: {ppo_clip_value:.3f}")
        print("Reward Breakdown:", episode_data[-1]['info'])

    # 训练结束后关闭 TensorBoard 写入器
    writer.close()

    return model, rewards_history, avg_rewards, best_model_state, best_avg_reward
