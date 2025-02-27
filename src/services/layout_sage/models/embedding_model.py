import torch
import torch.nn as nn
import torch.nn.functional as F

class AttentionLayer(nn.Module):
    def __init__(self, input_dim):
        super(AttentionLayer, self).__init__()
        self.attention = nn.Linear(input_dim, 1)

    def forward(self, x):
        attention_weights = F.softmax(self.attention(x), dim=1)
        return torch.sum(x * attention_weights, dim=1)

class EmbeddingModel(nn.Module):
    def __init__(self, num_users, num_times, num_locations, num_devices, num_layouts, 
                 embedding_dim):
        super(EmbeddingModel, self).__init__()
        
        # 特征嵌入层
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.time_embedding = nn.Embedding(num_times, embedding_dim)
        self.location_embedding = nn.Embedding(num_locations, embedding_dim)
        self.device_embedding = nn.Embedding(num_devices, embedding_dim)
        self.layout_embedding = nn.Embedding(num_layouts, embedding_dim)
        
        # 注意力层
        self.attention = AttentionLayer(embedding_dim)
        
        # 全连接层
        self.fc1 = nn.Linear(embedding_dim * 5, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, user_ids, time_ids, location_ids, device_ids, layout_ids):
        # 获取嵌入
        user_embed = self.attention(self.user_embedding(user_ids).unsqueeze(1))
        time_embed = self.attention(self.time_embedding(time_ids).unsqueeze(1))
        location_embed = self.attention(self.location_embedding(location_ids).unsqueeze(1))
        device_embed = self.attention(self.device_embedding(device_ids).unsqueeze(1))
        layout_embed = self.attention(self.layout_embedding(layout_ids).unsqueeze(1))

        # 连接所有特征
        x = torch.cat([user_embed, time_embed, location_embed, device_embed, layout_embed], 
                     dim=1)
        
        # 通过全连接层
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        
        return self.fc3(x)