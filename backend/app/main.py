from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.routes import router


app = FastAPI(
    title="CodeGuard AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.app_env,
        "provider": settings.ai_provider,
    }


try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None