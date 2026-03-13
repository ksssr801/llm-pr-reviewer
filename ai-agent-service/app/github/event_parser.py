from app.config import get_settings
from app.logger_config import get_logger
from app.schemas.webhook_models import WebhookPayload

settings = get_settings()

logger = get_logger(__name__)


def should_trigger_review(payload: WebhookPayload) -> bool:
    """
    Determines whether an AI review should run.
    """

    action = payload.action

    label_name = None
    if payload.label:
        label_name = payload.label.name
    logger.info(f"Action: {action}, Label: {label_name}")

    # if action == "opened":
    #     return True

    # if action == "synchronize":
    #     return True

    if action == "labeled" and label_name.startswith(settings.ai_review_label):
        return (True, extract_review_mode(label_name))

    return (False, "brief")


def extract_review_mode(label: str) -> str:
    """
    Extracts the review mode from the payload.
    """
    if not label:
        return "brief"
    if "ai-review:deep" in label:
        return "deep"
    if "ai-review:standard" in label:
        return "standard"
    return "brief"
