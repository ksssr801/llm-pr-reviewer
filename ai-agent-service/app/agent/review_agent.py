from app.config import get_settings
from app.github.github_client import GitHubClient
from app.logger_config import get_logger
from app.services.chunking_service import ChunkingService
from app.services.diff_extractor import DiffExtractor
from app.services.llm_review_service import LLMReviewService
from app.state.review_state_manager import ReviewStateManager

logger = get_logger(__name__)
state_manager = ReviewStateManager()


async def start_review(repo: str, pr_number: int, review_mode: str):
    """
    Entry point for the AI code review pipeline.
    """

    settings = get_settings()
    client = GitHubClient()
    logger.info(
        "Starting AI review",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "model": settings.llm_model,
            "review_mode": review_mode,
        },
    )

    # ---------------------------------------------------
    # Step 1: Fetch PR metadata
    # ---------------------------------------------------
    pr = await client.get_pull_request(repo, pr_number)
    head_sha = pr["head"]["sha"]
    logger.info(
        "Fetched PR metadata",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "head_sha": head_sha,
        },
    )

    # ---------------------------------------------------
    # Step 2: Check last reviewed commit (Redis)
    # ---------------------------------------------------
    last_sha = await state_manager.get_last_reviewed_sha(repo, pr_number)
    if last_sha == head_sha:
        logger.info(
            "Skipping review — commit already reviewed",
            extra={
                "repository": repo,
                "pull_request": pr_number,
                "sha": head_sha,
            },
        )
        return

    # ---------------------------------------------------
    # Step 3: Decide which files to review
    # ---------------------------------------------------
    if last_sha:
        logger.info(
            "Running incremental review",
            extra={
                "repository": repo,
                "pull_request": pr_number,
                "base_sha": last_sha,
                "head_sha": head_sha,
            },
        )
        compare_data = await client.compare_commits(
            repo,
            last_sha,
            head_sha,
        )
        files = compare_data["files"]
    else:
        logger.info(
            "First review for this PR",
            extra={
                "repository": repo,
                "pull_request": pr_number,
            },
        )
        files = await client.get_pull_request_files(repo, pr_number)
    logger.info(
        "PR files fetched",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "files": len(files),
        },
    )

    # ---------------------------------------------------
    # Step 4: Extract diffs
    # ---------------------------------------------------
    diffs = DiffExtractor.extract(files)
    logger.info(
        "Diffs extracted",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "diffs": len(diffs),
        },
    )

    # ---------------------------------------------------
    # Step 5: Chunk diffs
    # ---------------------------------------------------
    chunks = ChunkingService.chunk_diffs(diffs)
    logger.info(
        "Chunks created",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "chunks": len(chunks),
        },
    )

    # ---------------------------------------------------
    # Step 6: LLM review
    # ---------------------------------------------------
    comments = await LLMReviewService.review_chunks(chunks, review_mode)
    logger.info(
        "LLM review complete",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "comments": len(comments),
        },
    )

    # ---------------------------------------------------
    # Step 7: Post review comments
    # ---------------------------------------------------
    for comment in comments:
        await client.create_review_comment(
            repo,
            pr_number,
            comment,
            head_sha,
        )
    logger.info(
        "Comments posted to GitHub",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "comments": len(comments),
        },
    )

    # ---------------------------------------------------
    # Step 8: Save latest reviewed commit
    # ---------------------------------------------------
    await state_manager.set_last_reviewed_sha(
        repo,
        pr_number,
        head_sha,
    )

    logger.info(
        "Review state updated",
        extra={
            "repository": repo,
            "pull_request": pr_number,
            "stored_sha": head_sha,
        },
    )
