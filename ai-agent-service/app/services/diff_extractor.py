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

            lines = patch.split("\n")
            line_number = None
            current_line = None

            for line in lines:
                if line.startswith("@@"):
                    parts = line.split(" ")
                    new_file_part = parts[2]
                    current_line = int(new_file_part.split(",")[0][1:])
                    continue

                if line.startswith("+") and not line.startswith("+++"):
                    line_number = current_line
                    break

                if not line.startswith("-"):
                    current_line += 1

            if line_number is None:
                line_number = 1

            diff = FileDiff(
                filename=file["filename"],
                status=file.get("status", "unknown"),
                patch=patch,
                additions=file.get("additions", 0),
                deletions=file.get("deletions", 0),
                line=line_number,
                side="right",
            )
            diffs.append(diff)

        logger.info(
            "Diff extraction complete",
            total_files=len(diffs),
        )
        return diffs
