from app.agent.review_agent import start_review
from app.github.event_parser import should_trigger_review
from app.logger_config import get_logger
from app.schemas.webhook_models import WebhookPayload
from app.security.github_webhook_verifier import verify_github_signature
from fastapi import APIRouter, Request

logger = get_logger(__name__)

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.post("/webhook")
async def github_webhook(request: Request):

    body = await request.body()

    verify_github_signature(request, body)

    event_type = request.headers.get("X-GitHub-Event")
    payload_dict = await request.json()

    # Handle ping event
    if event_type == "ping":
        logger.info("Ping received from GitHub")
        return {"status": "ok"}

    if event_type != "pull_request":
        logger.info(f"Event type {event_type} is not supported")
        return {"status": "ignored"}

    payload = WebhookPayload.model_validate(payload_dict)

    logger.info(
        f"Webhook received: action={payload.action}, repo={payload.repository.full_name}"
    )

    trigger, review_mode = should_trigger_review(payload)
    if trigger:

        await start_review(
            repo=payload.repository.full_name,
            pr_number=payload.pull_request.number,
            review_mode=review_mode,
        )

    return {"status": "received"}
