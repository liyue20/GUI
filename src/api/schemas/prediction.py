from pydantic import BaseModel

class UserFeatures(BaseModel):
    user_identity: str
    time_of_day: str
    location: str
    device_type: str

class PredictionRequest(BaseModel):
    user_features: UserFeatures

class PredictionResponse(BaseModel):
    predicted_layout: str