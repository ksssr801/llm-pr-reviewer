from dataclasses import dataclass


@dataclass(slots=True)
class DiffChunk:
    """
    Represents a chunk of a diff suitable for LLM review.
    """

    filename: str
    content: str
    chunk_index: int
    line: int
