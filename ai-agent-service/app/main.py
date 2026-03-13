import contextlib

import uvicorn
from app.chat.chat_router import router as chat_router
from app.config import Settings, get_settings
from app.github.webhook_router import router as github_router
from app.infra.redis_client import init_redis
from app.logger_config import configure_logging, get_logger
from fastapi import FastAPI

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Lifecycle & Application Setup
# ------------------------------------------------------------------------------
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    configure_logging()
    await init_redis()
    settings = get_settings()
    logger.info("Starting AI Agent Service", env=settings.environment, version="0.1.0")
    yield

    # Shutdown actions
    logger.info("Shutting down AI Agent Service")


app = FastAPI(
    title="AI Code Review Agent",
    description="Backend AI service for code reviews and GitHub integration.",
    version="0.1.0",
    lifespan=lifespan,
)

# Register GitHub webhook router
app.include_router(github_router)

# Register chat router
app.include_router(chat_router)


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic health check endpoint to verify service is running.
    """
    logger.info("Health check")
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
