import torch

class EmbeddingPredictor:
    def __init__(self, model, user_encoder, time_encoder, location_encoder, device_encoder, layout_encoder):
        self.model = model
        self.user_encoder = user_encoder
        self.time_encoder = time_encoder
        self.location_encoder = location_encoder
        self.device_encoder = device_encoder
        self.layout_encoder = layout_encoder

    def predict(self, user_features):
        user_id = self.user_encoder.encode(user_features['user_identity'])
        time_id = self.time_encoder.encode(user_features['time_of_day'])
        location_id = self.location_encoder.encode(user_features['location'])
        device_id = self.device_encoder.encode(user_features['device_type'])

        best_layout = None
        max_score = float('-inf')
        for layout_id in range(len(self.layout_encoder.id_to_layout)):
            with torch.no_grad():
                score = self.model(
                    torch.tensor([user_id]), 
                    torch.tensor([time_id]), 
                    torch.tensor([location_id]), 
                    torch.tensor([device_id]), 
                    torch.tensor([layout_id])
                ).item()
            if score > max_score:
                max_score = score
                best_layout = layout_id
        return self.layout_encoder.decode(best_layout)