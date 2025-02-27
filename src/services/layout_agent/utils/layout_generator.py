import torch
import torch.nn.functional as F
import numpy as np
from src.services.layout_agent.enviroment.layout_environment import LayoutEnvironment

def generate_layout(model, card_width, card_height, blocks, num_attempts=5, max_steps=10):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    if len(blocks) <= 1:
        return blocks

    env = LayoutEnvironment(card_width, card_height, blocks)
    
    best_positions = None
    best_reward = float('-inf')
    
    for _ in range(num_attempts):
        positions, reward = generate_single_layout(model, env, max_steps, device)
        if reward > best_reward:
            best_reward = reward
            best_positions = positions
    
    return best_positions

def generate_single_layout(model, env, max_steps=100, device=None, 
                         initial_temperature=1.0, temperature_decay=0.95):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    state, initial_reward = env.reset()
    best_reward = float('-inf')
    best_positions = None
    no_improvement_count = 0
    total_reward = initial_reward
    temperature = initial_temperature

    for step in range(max_steps):
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
        
        with torch.no_grad():
            block_logits, action_logits, _ = model(state_tensor)
            block_probs = F.softmax(block_logits / temperature, dim=-1).cpu().numpy()
            action_probs = F.softmax(action_logits / temperature, dim=-1).cpu().numpy()

        block_selection = np.random.choice(len(block_probs[0]), p=block_probs[0])
        action_selection = np.random.choice(len(action_probs[0]), p=action_probs[0])
        
        state, reward, done, _ = env.step(block_selection, action_selection)
        total_reward += reward
        
        if total_reward > best_reward:
            best_reward = total_reward
            best_positions = env.positions.copy()
            no_improvement_count = 0
        else:
            no_improvement_count += 1
        
        temperature *= temperature_decay
        
        if no_improvement_count >= 10 or done:
            break
    
    return best_positions, best_reward