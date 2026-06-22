from fastapi import FastAPI
from app.api.endpoints import router as extract_router
from app.core.config import settings
from app.core.security import limiter
# pyrefly: ignore [missing-import]
from slowapi import _rate_limit_exceeded_handler
# pyrefly: ignore [missing-import]
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(extract_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "docs_url": "/docs"
    }