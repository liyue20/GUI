import os
import torch
from functools import lru_cache
from src.services.layout_agent.models.layout_model import DynamicPPONetwork
from src.services.layout_sage.models.embedding_model import EmbeddingModel
from src.services.layout_sage.predictors.embedding_predictor import EmbeddingPredictor

@lru_cache()
def get_layout_model():
    model = DynamicPPONetwork()
    model_path = os.path.join('data', 'models', 'layout', 'layoutModel_05.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

@lru_cache()
def get_embedding_model():
    model = EmbeddingModel(
        num_users=100,
        num_times=24,
        num_locations=50,
        num_devices=10,
        num_layouts=5,
        embedding_dim=32
    )
    model_path = os.path.join('data', 'models', 'layout_sage', 'embedding_model.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

@lru_cache()
def get_embedding_predictor():
    model = get_embedding_model()
    # 加载所需的编码器
    utils_path = os.path.join('data', 'models', 'layout_sage', 'embedding_model_utils.pth')
    utils = torch.load(utils_path)
    
    return EmbeddingPredictor(
        model,
        utils['user_encoder'],
        utils['time_encoder'],
        utils['location_encoder'],
        utils['device_encoder'],
        utils['layout_encoder']
    )
