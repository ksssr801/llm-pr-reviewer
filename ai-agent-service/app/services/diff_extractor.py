from typing import Dict, List

from app.domain.diff_models import FileDiff
from app.logger_config import get_logger

logger = get_logger(__name__)


class DiffExtractor:
    """
    Converts raw GitHub API responses into structured FileDiff objects.
    """

    @staticmethod
    def extract(pr_files: List[Dict]) -> List[FileDiff]:
        """
        Extract diff information from GitHub pull request files.

        Parameters
        ----------
        pr_files : List[Dict]
            Raw response from GitHub API.

        Returns
        -------
        List[FileDiff]
            Structured diff objects.
        """

        diffs: List[FileDiff] = []

        for file in pr_files:

            patch = file.get("patch")

            if not patch:
                logger.info(
                    "Skipping file without patch",
                    file=file.get("filename"),
                    status=file.get("status"),
                )
                continue

            diff = FileDiff(
                filename=file["filename"],
                status=file.get("status", "unknown"),
                patch=patch,
                additions=file.get("additions", 0),
                deletions=file.get("deletions", 0),
            )

            diffs.append(diff)

        logger.info(
            "Diff extraction complete",
            total_files=len(diffs),
        )

        return diffs
