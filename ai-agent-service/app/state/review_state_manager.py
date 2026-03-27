from app.infra.redis_client import get_redis
from app.logger_config import get_logger

logger = get_logger(__name__)


class ReviewStateManager:
    """
    Stores and retrieves last reviewed commit SHA for a PR.
    """

    def _key(self, repo: str, pr_number: int) -> str:
        return f"review_state:{repo}:{pr_number}"

    async def get_last_reviewed_sha(self, repo: str, pr_number: int):
        redis = get_redis()
        key = self._key(repo, pr_number)
        sha = await redis.get(key)
        logger.info(
            "Fetched review state",
            repository=repo,
            pull_request=pr_number,
            last_sha=sha,
        )
        return sha

    async def set_last_reviewed_sha(self, repo: str, pr_number: int, sha: str):
        redis = get_redis()
        key = self._key(repo, pr_number)
        await redis.set(key, sha)
        logger.info(
            "Stored review state",
            repository=repo,
            pull_request=pr_number,
            sha=sha,
        )
