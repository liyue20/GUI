from typing import Dict, List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import deque
import random

class StyleModel(nn.Module):
    """样式优化模型"""
    
    def __init__(self, state_dim: int, action_size: int, hidden_size: int = 128):
        super(StyleModel, self).__init__()
        
        # 网络结构
        self.fc1 = nn.Linear(state_dim, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
        
        # 经验回放缓冲区
        self.memory = deque(maxlen=2000)
        
        # 训练参数
        self.batch_size = 32
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)
    
    def encode_state(self, state: Dict) -> np.ndarray:
        """将状态编码为向量"""
        encoded = []
        
        # 编码颜色信息
        for color_name, color_value in state['style']['colors'].items():
            # 将颜色转换为RGB值
            rgb = self._hex_to_rgb(color_value)
            encoded.extend(rgb)
        
        # 编码分数
        encoded.append(state['score'])
        
        # 编码历史分数
        history_scores = state['history_scores']
        # 填充到固定长度
        while len(history_scores) < 5:
            history_scores.append(0)
        encoded.extend(history_scores[-5:])
        
        # 编码当前步数
        encoded.append(state['step'] / 20.0)  # 归一化
        
        return np.array(encoded, dtype=np.float32)
    
    def _hex_to_rgb(self, hex_color: str) -> List[float]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    def choose_action(self, state: Dict, training: bool = True) -> int:
        """选择动作"""
        state_vector = self.encode_state(state)
        state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
        
        if training and random.random() < self.epsilon:
            # 探索：随机选择动作
            return random.randrange(self.fc3.out_features)
        
        with torch.no_grad():
            # 利用：选择Q值最大的动作
            q_values = self.forward(state_tensor)
            return torch.argmax(q_values).item()
    
    def remember(self, state: Dict, action: int, reward: float, 
                next_state: Dict, done: bool):
        """存储经验"""
        # 编码状态
        state_vector = self.encode_state(state)
        next_state_vector = self.encode_state(next_state)
        
        self.memory.append((
            state_vector, action, reward, next_state_vector, done
        ))
    
    def replay(self) -> float:
        """训练模型"""
        if len(self.memory) < self.batch_size:
            return 0.0
            
        # 采样batch
        minibatch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor([x[0] for x in minibatch])
        actions = torch.LongTensor([x[1] for x in minibatch])
        rewards = torch.FloatTensor([x[2] for x in minibatch])
        next_states = torch.FloatTensor([x[3] for x in minibatch])
        dones = torch.FloatTensor([x[4] for x in minibatch])
        
        # 计算当前Q值
        current_q_values = self.forward(states).gather(1, actions.unsqueeze(1))
        
        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.forward(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
            
        # 计算损失
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # 更新模型
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 更新探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return loss.item()
    
    def save(self, path: str):
        """保存模型"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)
    
    def load(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']