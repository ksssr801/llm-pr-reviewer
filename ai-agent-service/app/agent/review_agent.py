from app.config import get_settings
from app.github.github_client import GitHubClient
from app.logger_config import get_logger
from app.services.chunking_service import ChunkingService
from app.services.diff_extractor import DiffExtractor
from app.services.llm_review_service import LLMReviewService

logger = get_logger(__name__)


async def start_review(repo: str, pr_number: int):
    """
    Entry point for the AI code review pipeline.
    """

    settings = get_settings()

    logger.info(
        "Starting AI review",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "model": settings.llm_model,
        },
    )

    client = GitHubClient()
    files = await client.get_pull_request_files(repo, pr_number)

    logger.info(
        "PR files fetched",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "files": len(files),
        },
    )

    diffs = DiffExtractor.extract(files)
    logger.info(
        "Diffs extracted",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "diffs": len(diffs),
        },
    )

    chunks = ChunkingService.chunk_diffs(diffs)
    logger.info(
        "Chunks created",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "chunks": len(chunks),
        },
    )

    comments = await LLMReviewService.review_chunks(chunks)

    # fetch commit id
    pr = await client.get_pull_request(repo, pr_number)
    commit_id = pr["head"]["sha"]

    # post comments
    for comment in comments:
        await client.create_review_comment(repo, pr_number, comment, commit_id)

    logger.info(
        "Comments generated",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "comments": len(comments),
        },
    )

    # Future pipeline
    # 1 fetch PR diff
    # 2 parse files
    # 3 chunk large diffs
    # 4 send to LLM
    # 5 parse feedback
    # 6 post comments

    logger.info(
        "Review pipeline initialized",
        extra={"repository": repo, "pull_request": pr_number},
    )
