import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.nn import TransformerEncoder, TransformerEncoderLayer

class DynamicPPONetwork_old(nn.Module):
    def __init__(self, embedding_dim=64, hidden_dim=256, num_layers=2):
        super(DynamicPPONetwork, self).__init__()
        self.embedding = nn.Linear(7, embedding_dim)

        encoder_layers = TransformerEncoderLayer(embedding_dim, 8, hidden_dim)
        self.transformer_encoder = TransformerEncoder(encoder_layers, num_layers)

        self.shared = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        self.actor_block = nn.Linear(hidden_dim, 1)
        self.actor_action = nn.Linear(hidden_dim, 8)
        self.critic = nn.Linear(hidden_dim, 1)

    def forward(self, state):
        embedded = self.embedding(state)
        attended = self.transformer_encoder(embedded)
        features = self.shared(attended)
        
        block_logits = self.actor_block(features).squeeze(-1)
        action_logits = self.actor_action(features.mean(dim=1))
        value = self.critic(features.mean(dim=1))
        return block_logits, action_logits, value



class DynamicPPONetwork(nn.Module):
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
    

    