import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler  # pyrefly: ignore[missing-import]
from slowapi.errors import RateLimitExceeded  # pyrefly: ignore[missing-import]

from app.api.endpoints import router as extract_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.security import limiter

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(extract_router, prefix="/api/v1")

@app.get("/", tags=["UI"], include_in_schema=False)
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))