
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
class DynamicPPONetwork(nn.Module):
    def __init__(self, embedding_dim=64, hidden_dim=256):
        super(DynamicPPONetwork, self).__init__()
        # 输入特征维度7（每个区块的特征）
        self.embedding = nn.Linear(7, embedding_dim)
        # 多头注意力机制（不使用 batch_first，确保输入维度正确）
        self.attention = nn.MultiheadAttention(embedding_dim, num_heads=8, dropout=0.1)
        # 前馈网络，使用LayerNorm和Dropout增强稳定性并防止过拟合
        self.shared = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        )
        # Actor分支：输出block选择和动作选择的logits
        self.actor_block = nn.Linear(hidden_dim, 1)
        self.actor_action = nn.Linear(hidden_dim, 8)
        # Critic分支：输出状态价值估计
        self.critic = nn.Linear(hidden_dim, 1)
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0)

    def forward(self, state):
        # state 维度: [batch_size, num_blocks, feature_dim(7)]
        batch_size, num_blocks, _ = state.shape
        # 对每个block的特征做线性嵌入
        embedded = self.embedding(state)
        # 将输入的 batch 转置为 (seq_len, batch, embed_dim) 以兼容旧版 PyTorch
        embedded = embedded.transpose(0, 1)  # 转换为 (num_blocks, batch_size, embedding_dim)
        # 通过多头注意力获取block间相关特征
        attended, _ = self.attention(embedded, embedded, embedded)
        # 还原为 (batch_size, num_blocks, hidden_dim) 形状
        features = self.shared(attended.view(-1, attended.size(-1))).view(batch_size, num_blocks, -1)
        # block选择的得分（每个block一个分值）
        block_logits = self.actor_block(features).squeeze(-1)     # [batch_size, num_blocks]
        # 动作选择的得分（基于所有block的平均特征）
        avg_features = features.mean(dim=1)                      # [batch_size, hidden_dim]
        action_logits = self.actor_action(avg_features)          # [batch_size, 8]
        value = self.critic(avg_features)                        # [batch_size, 1]
        return block_logits, action_logits, value

class DynamicPPONetwork_old_old(nn.Module):
    def __init__(self, embedding_dim=64, hidden_dim=256):
        super(DynamicPPONetwork, self).__init__()
        # 输入特征维度7（每个区块的特征）
        self.embedding = nn.Linear(7, embedding_dim)
        # 多头注意力机制，batch_first=True 并加入 dropout
        self.attention = nn.MultiheadAttention(embedding_dim, num_heads=8, batch_first=True, dropout=0.1)
        # 前馈网络，使用LayerNorm和Dropout增强稳定性并防止过拟合
        self.shared = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        )
        # Actor分支：输出block选择和动作选择的logits
        self.actor_block = nn.Linear(hidden_dim, 1)
        self.actor_action = nn.Linear(hidden_dim, 8)
        # Critic分支：输出状态价值估计
        self.critic = nn.Linear(hidden_dim, 1)
        self._init_weights()
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0)
    def forward(self, state):
        # state 维度: [batch_size, num_blocks, feature_dim(7)]
        batch_size, num_blocks, _ = state.shape
        # 对每个block的特征做线性嵌入
        embedded = self.embedding(state)
        # 通过多头注意力获取block间相关特征
        attended, _ = self.attention(embedded, embedded, embedded)
        # 前馈网络处理，每个block特征独立输入，输出再 reshape 回原形状
        features = self.shared(attended.reshape(-1, attended.size(-1))).reshape(batch_size, num_blocks, -1)
        # block选择的得分（每个block一个分值）
        block_logits = self.actor_block(features).squeeze(-1)     # [batch_size, num_blocks]
        # 动作选择的得分（基于所有block的平均特征）
        avg_features = features.mean(dim=1)                      # [batch_size, hidden_dim]
        action_logits = self.actor_action(avg_features)          # [batch_size, 8]
        value = self.critic(avg_features)                        # [batch_size, 1]
        return block_logits, action_logits, value

class DynamicPPONetwork_old(nn.Module):
    def __init__(self, embedding_dim=64, hidden_dim=256):
        super(DynamicPPONetwork, self).__init__()
        self.embedding = nn.Linear(7, embedding_dim)
        self.attention = nn.MultiheadAttention(embedding_dim, 8)
        self.shared = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU()
        )
        self.actor_block = nn.Linear(hidden_dim, 1)
        self.actor_action = nn.Linear(hidden_dim, 8)
        self.critic = nn.Linear(hidden_dim, 1)
        
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0)

    def forward(self, state):
        batch_size, num_blocks, _ = state.shape
        embedded = self.embedding(state)
        attended, _ = self.attention(embedded, embedded, embedded)
        features = self.shared(attended.view(-1, attended.size(-1))).view(batch_size, num_blocks, -1)
        
        block_logits = self.actor_block(features).squeeze(-1)
        action_logits = self.actor_action(features.mean(dim=1))
        value = self.critic(features.mean(dim=1))
        return block_logits, action_logits, value