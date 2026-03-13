from typing import List

from app.domain.chunk_models import DiffChunk
from app.domain.diff_models import FileDiff
from app.logger_config import get_logger

logger = get_logger(__name__)

MAX_CHUNK_SIZE = 1500


class ChunkingService:
    """
    Splits large diffs into smaller chunks suitable for LLM processing.
    """

    @staticmethod
    def chunk_diffs(diffs: List[FileDiff]) -> List[DiffChunk]:

        chunks: List[DiffChunk] = []

        for diff in diffs:
            patch = diff.patch
            start = 0
            index = 0

            while start < len(patch):
                end = start + MAX_CHUNK_SIZE
                chunk_content = patch[start:end]
                chunk = DiffChunk(
                    filename=diff.filename,
                    content=chunk_content,
                    chunk_index=index,
                )
                chunks.append(chunk)
                index += 1
                start = end

        logger.info(
            "Chunking complete",
            total_chunks=len(chunks),
        )

        return chunks
