from typing import List

from app.agent.llm import generate_response
from app.config import get_settings
from app.domain.chunk_models import DiffChunk
from app.domain.review_models import ReviewComment
from app.logger_config import get_logger

logger = get_logger(__name__)

BRIEF_PROMPT = """
You are a senior engineer performing a BRIEF AI code review.

Your output MUST start with:
[AI REVIEW - BRIEF]

Return concise issues only.

Format:

Category
- file: <file>
  issue: <short description>

Categories:
Bug
Security
Performance
Suggestion

Keep output very short.
"""

STANDARD_PROMPT = """
You are a senior engineer performing a STANDARD AI code review.

Your output MUST start with:
[AI REVIEW - STANDARD]

Identify:
- Bugs
- Security risks
- Performance problems
- Readability issues

Format:

Category
File:
Issue:
Suggestion:

Keep the review concise.
"""

DEEP_PROMPT = """
You are a senior engineer performing a DEEP AI code review.

Your output MUST start with:
[AI REVIEW - DEEP]

Analyze:
- correctness
- architecture
- security
- performance
- maintainability

Explain issues and give improvement suggestions.
"""


class LLMReviewService:
    """
    Sends code chunks to the LLM and converts responses into review comments.
    """

    @staticmethod
    async def review_chunks(
        chunks: List[DiffChunk], review_mode: str
    ) -> List[ReviewComment]:

        settings = get_settings()

        comments: List[ReviewComment] = []

        for chunk in chunks:

            prompt = LLMReviewService._build_prompt(chunk, review_mode)

            response = await generate_response(prompt, settings)

            comment = ReviewComment(
                filename=chunk.filename,
                comment=response,
                severity="info",
                line=chunk.line,
            )

            comments.append(comment)

        logger.info(
            "LLM review complete",
            comment_count=len(comments),
        )

        return comments

    @staticmethod
    def _build_prompt(chunk: DiffChunk, review_mode: str) -> str:
        """
        Construct prompt sent to the LLM.
        """

        template = LLMReviewService._get_prompt(review_mode)
        return f"""
            {template}
            File: {chunk.filename}
            Diff: {chunk.content}
        """

    @staticmethod
    def _get_prompt(review_mode: str) -> str:
        if review_mode == "brief":
            return BRIEF_PROMPT
        elif review_mode == "standard":
            return STANDARD_PROMPT
        elif review_mode == "deep":
            return DEEP_PROMPT
        else:
            raise ValueError(f"Invalid review mode: {review_mode}")
