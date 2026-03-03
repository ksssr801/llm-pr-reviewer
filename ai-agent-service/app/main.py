import contextlib

import uvicorn
from app.config import Settings, get_settings
from app.logging import configure_logging, get_logger
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel


# ------------------------------------------------------------------------------
# Request & Response Models
# ------------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None


# ------------------------------------------------------------------------------
# Lifecycle & Application Setup
# ------------------------------------------------------------------------------
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    configure_logging()
    logger = get_logger(__name__)
    settings = get_settings()
    logger.info("Starting AI Agent Service", env=settings.environment, version="0.1.0")

    yield

    # Shutdown actions
    logger.info("Shutting down AI Agent Service")


app = FastAPI(
    title="Leave Policy AI Agent Service",
    description="Backend AI service for navigating and answering leave policy queries.",
    version="0.1.0",
    lifespan=lifespan,
)


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic health check endpoint to verify service is running.
    """
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat_endpoint(
    request: ChatRequest, settings: Settings = Depends(get_settings)
):
    """
    Main endpoint for communicating with the AI Agent.
    """
    logger = get_logger(__name__)
    logger.info(
        "Received chat request",
        session_id=request.session_id,
        request_length=len(request.message),
    )

    # TODO: Connect this to the actual AI Agent Orchestrator (Phase 3+)
    placeholder_reply = f"Hello! This is the AI Agent placeholder. I received your message: '{request.message}'"

    return ChatResponse(reply=placeholder_reply, session_id=request.session_id)


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )

