from dataclasses import dataclass


@dataclass(slots=True)
class FileDiff:
    """
    Represents a single file diff extracted from a pull request.
    """

    filename: str
    status: str
    patch: str
    additions: int
    deletions: int

    @property
    def change_size(self) -> int:
        """
        Total number of changed lines.
        """
        return self.additions + self.deletions
