from typing import List

from app.agent.llm import generate_response
from app.config import get_settings
from app.domain.chunk_models import DiffChunk
from app.domain.review_models import ReviewComment
from app.logger_config import get_logger

logger = get_logger(__name__)


class LLMReviewService:
    """
    Sends code chunks to the LLM and converts responses into review comments.
    """

    @staticmethod
    async def review_chunks(chunks: List[DiffChunk]) -> List[ReviewComment]:

        settings = get_settings()

        comments: List[ReviewComment] = []

        for chunk in chunks:

            prompt = LLMReviewService._build_prompt(chunk)

            response = await generate_response(prompt, settings)

            comment = ReviewComment(
                filename=chunk.filename,
                comment=response,
                severity="info",
            )

            comments.append(comment)

        logger.info(
            "LLM review complete",
            comment_count=len(comments),
        )

        return comments

    @staticmethod
    def _build_prompt(chunk: DiffChunk) -> str:
        """
        Construct prompt sent to the LLM.
        """

        return f"""
            You are an expert software engineer performing a code review.

            Review the following diff and identify:
            - bugs
            - security issues
            - performance problems
            - readability improvements

            File: {chunk.filename}

            Diff:
            {chunk.content}

            Provide concise feedback.
        """
