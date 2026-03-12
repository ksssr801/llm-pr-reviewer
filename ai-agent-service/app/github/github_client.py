import httpx
from app.config import get_settings
from app.logger_config import get_logger

logger = get_logger(__name__)


class GitHubClient:

    def __init__(self):
        self.settings = get_settings()

        self.token = self.settings.github_token

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    async def get_pull_request_files(self, repo: str, pr_number: int):

        url = f"{self.settings.github_api_base}/repos/{repo}/pulls/{pr_number}/files"

        logger.info(
            "Fetching PR files",
            repository=repo,
            pull_request=pr_number,
        )

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                headers=self.headers,
            )

        response.raise_for_status()

        return response.json()
