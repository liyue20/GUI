import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.layout_sage.models.embedding_model import EmbeddingModel
from  src.services.layout_sage.data_fetcher.fetch_data import get_or_generate_data
from src.services.layout_sage.utils.preprocessor import preprocess_data

def train_embedding_model(train_loader, val_loader, num_users, num_times, num_locations, num_devices, num_layouts, embedding_dim, epochs=200):
    model = EmbeddingModel(num_users, num_times, num_locations, num_devices, num_layouts, embedding_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.5, verbose=True)

    best_val_loss = float('inf')
    patience = 30
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for user_ids, time_ids, location_ids, device_ids, layout_ids, usage_times in train_loader:
            optimizer.zero_grad()
            outputs = model(user_ids, time_ids, location_ids, device_ids, layout_ids)
            loss = criterion(outputs, usage_times)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        avg_train_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for user_ids, time_ids, location_ids, device_ids, layout_ids, usage_times in val_loader:
                outputs = model(user_ids, time_ids, location_ids, device_ids, layout_ids)
                loss = criterion(outputs, usage_times)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)
        
        print(f'Epoch {epoch+1}/{epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')
        
        scheduler.step(avg_val_loss)
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), 'best_embedding_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

    return model

def main():
    # Load or generate the data
    data = get_or_generate_data(num_samples=5000)
    
    # Preprocess the data
    processed_data, user_encoder, time_encoder, location_encoder, device_encoder, layout_encoder, scaler = preprocess_data(data)

    # Prepare data for training
    user_ids = torch.tensor([item['user_id'] for item in processed_data], dtype=torch.long)
    time_ids = torch.tensor([item['time_id'] for item in processed_data], dtype=torch.long)
    location_ids = torch.tensor([item['location_id'] for item in processed_data], dtype=torch.long)
    device_ids = torch.tensor([item['device_id'] for item in processed_data], dtype=torch.long)
    layout_ids = torch.tensor([item['layout_id'] for item in processed_data], dtype=torch.long)
    usage_times = torch.tensor([item['usage_time'] for item in processed_data], dtype=torch.float32).unsqueeze(1)

    # Normalize usage times
    usage_times_mean = usage_times.mean()
    usage_times_std = usage_times.std()
    normalized_usage_times = (usage_times - usage_times_mean) / usage_times_std

    # Split data into train and validation sets
    train_size = int(0.8 * len(user_ids))
    train_dataset = TensorDataset(user_ids[:train_size], time_ids[:train_size], location_ids[:train_size], 
                                  device_ids[:train_size], layout_ids[:train_size], normalized_usage_times[:train_size])
    val_dataset = TensorDataset(user_ids[train_size:], time_ids[train_size:], location_ids[train_size:], 
                                device_ids[train_size:], layout_ids[train_size:], normalized_usage_times[train_size:])

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    num_users = len(user_encoder.item_to_id)
    num_times = len(time_encoder.item_to_id)
    num_locations = len(location_encoder.item_to_id)
    num_devices = len(device_encoder.item_to_id)
    num_layouts = len(layout_encoder.item_to_id)
    embedding_dim = 32

    model = train_embedding_model(train_loader, val_loader, num_users, num_times, num_locations, num_devices, num_layouts, embedding_dim)

    # Save the trained model
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'models')
    os.makedirs(model_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_dir, 'embedding_model_with_attention.pth'))

    # Save the encoders, scaler and usage time normalizer
    torch.save({
        'user_encoder': user_encoder,
        'time_encoder': time_encoder,
        'location_encoder': location_encoder,
        'device_encoder': device_encoder,
        'layout_encoder': layout_encoder,
        'feature_scaler': scaler,
        'usage_time_mean': usage_times_mean,
        'usage_time_std': usage_times_std
    }, os.path.join(model_dir, 'embedding_model_utils.pth'))

if __name__ == "__main__":
    main()