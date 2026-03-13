from typing import List

import httpx
from app.config import get_settings
from app.domain.review_models import ReviewComment
from app.logger_config import get_logger

logger = get_logger(__name__)


class GitHubClient:

    def __init__(self):
        self.settings = get_settings()
        logger.info(
            "GitHub token loaded", token_present=bool(self.settings.github_token)
        )
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

    async def get_pull_request(self, repo: str, pr_number: int):
        """
        Fetch pull request metadata including commit SHA.
        """
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
            )
        response.raise_for_status()
        return response.json()

    async def create_review_comment(
        self,
        repo: str,
        pr_number: int,
        comment: ReviewComment,
        commit_id: str,
    ):
        """
        Post a review comment on a pull request.
        """
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
        payload = {
            "body": comment.comment,
            "commit_id": commit_id,
            "path": comment.filename,
            "line": comment.line,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
            )
        if response.status_code >= 400:
            logger.error(
                "GitHub API error while posting comment",
                status=response.status_code,
                response=response.text,
                file=comment.filename,
                line=comment.line,
            )
        response.raise_for_status()
        logger.info(
            "Posted review comment",
            file=comment.filename,
        )

    async def compare_commits(
        self,
        repo: str,
        base_sha: str,
        head_sha: str,
    ):
        """
        Fetch changes between two commits.
        """

        url = f"https://api.github.com/repos/{repo}/compare/{base_sha}...{head_sha}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
            )
        response.raise_for_status()
        return response.json()
