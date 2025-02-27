from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas.prediction import PredictionRequest, PredictionResponse
from src.services.layout_sage.predictors.embedding_predictor import EmbeddingPredictor
from src.api.dependencies import get_embedding_predictor

router = APIRouter(prefix="/predict", tags=["prediction"])

@router.post("/", response_model=PredictionResponse)
async def predict_layout(
    request: PredictionRequest,
    predictor: EmbeddingPredictor = Depends(get_embedding_predictor)
):
    try:
        user_features = {
            'user_identity': request.user_features.user_identity,
            'time_of_day': request.user_features.time_of_day,
            'location': request.user_features.location,
            'device_type': request.user_features.device_type
        }
        
        predicted_layout = predictor.predict(user_features)
        return PredictionResponse(predicted_layout=predicted_layout)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during prediction: {str(e)}"
        )