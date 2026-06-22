from fastapi import FastAPI
from app.api.endpoints import router as extract_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)
app.include_router(extract_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "docs_url": "/docs"
    }