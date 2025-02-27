import csv
import random
import os
from src.utils.logging import setup_logger

logger = setup_logger('layout_sage_data')

def generate_sample_data(num_samples=100):
    """生成样本数据"""
    user_identities = ['user1', 'user2', 'user3', 'user4', 'user5']
    times_of_day = ['morning', 'afternoon', 'evening', 'night']
    locations = ['home', 'office', 'cafe', 'outdoors']
    device_types = ['mobile', 'tablet', 'laptop', 'desktop']
    layouts = [
        "H1:H2, padding: 10px",
        "H1:H3, margin: 15px",
        "H2:H4, border: 1px solid",
        "H1:H4, display: flex",
        "H2:H3, text-align: center"
    ]

    data = []
    for _ in range(num_samples):
        sample = {
            'user_identity': random.choice(user_identities),
            'time_of_day': random.choice(times_of_day),
            'location': random.choice(locations),
            'device_type': random.choice(device_types),
            'layout': random.choice(layouts),
            'usage_time': random.uniform(0, 168)
        }
        data.append(sample)

    return data

def get_or_generate_data(num_samples=100):
    """获取或生成数据"""
    dataset_dir = os.path.join(os.getcwd(), 'data', 'datasets')
    os.makedirs(dataset_dir, exist_ok=True)
    
    dataset_path = os.path.join(dataset_dir, 'layout_dataset.csv')
    
    if os.path.exists(dataset_path):
        logger.info(f"Loading existing dataset from {dataset_path}")
        return load_data(dataset_path)
    else:
        logger.info(f"Generating new dataset with {num_samples} samples")
        data = generate_sample_data(num_samples)
        save_data(data, dataset_path)
        return data

def save_data(data, filename):
    """保存数据到CSV文件"""
    with open(filename, 'w', newline='') as f:
        fields = ['user_identity', 'time_of_day', 'location', 'device_type', 
                 'layout', 'usage_time']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def load_data(filename):
    """从CSV文件加载数据"""
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)