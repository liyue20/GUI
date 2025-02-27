from sklearn.preprocessing import StandardScaler
from collections import defaultdict

class LabelEncoder:
    def __init__(self):
        self.item_to_id = {}
        self.id_to_item = {}
        self.current_id = 0
    
    def fit(self, items):
        unique_items = set(items)
        for item in unique_items:
            if item not in self.item_to_id:
                self.item_to_id[item] = self.current_id
                self.id_to_item[self.current_id] = item
                self.current_id += 1
    
    def encode(self, item):
        return self.item_to_id.get(item, -1)
    
    def decode(self, id):
        return self.id_to_item.get(id)

def preprocess_data(data):
    # 创建编码器
    user_encoder = LabelEncoder()
    time_encoder = LabelEncoder()
    location_encoder = LabelEncoder()
    device_encoder = LabelEncoder()
    layout_encoder = LabelEncoder()
    
    # 拟合编码器
    user_encoder.fit([item['user_identity'] for item in data])
    time_encoder.fit([item['time_of_day'] for item in data])
    location_encoder.fit([item['location'] for item in data])
    device_encoder.fit([item['device_type'] for item in data])
    layout_encoder.fit([item['layout'] for item in data])
    
    # 创建标准化器
    scaler = StandardScaler()
    
    # 处理数据
    processed_data = []
    usage_times = [[float(item['usage_time'])] for item in data]
    scaled_usage_times = scaler.fit_transform(usage_times)
    
    for idx, item in enumerate(data):
        processed_item = {
            'user_id': user_encoder.encode(item['user_identity']),
            'time_id': time_encoder.encode(item['time_of_day']),
            'location_id': location_encoder.encode(item['location']),
            'device_id': device_encoder.encode(item['device_type']),
            'layout_id': layout_encoder.encode(item['layout']),
            'usage_time': scaled_usage_times[idx][0]
        }
        processed_data.append(processed_item)
    
    return (processed_data, user_encoder, time_encoder, location_encoder, 
            device_encoder, layout_encoder, scaler)