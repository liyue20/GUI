from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import layout_api, prediction, style_api  

app = FastAPI(
    title="AIGUI Model Service",
    description="AI GUI Layout and Style Generation Service",
    version="1.0.1"
)

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(layout_api.router, prefix="/api/layout", tags=["layout"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(style_api.router, prefix="/api/style", tags=["style"])

@app.get("/health/check")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "layout_agent": "running",
            "layout_sage": "running"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    