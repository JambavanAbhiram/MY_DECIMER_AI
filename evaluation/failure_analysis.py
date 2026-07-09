"""
evaluation/failure_analysis.py

Utilities for collecting, summarizing, and exporting
pipeline failures during evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from evaluation.config import REPORTS_DIR


@dataclass
class FailureRecord:
    """
    Represents a single pipeline failure.
    """

    timestamp: str
    stage: str
    error_type: str
    message: str
    document_id: Optional[str] = None
    image_id: Optional[str] = None
    file_path: Optional[str] = None


class FailureAnalyzer:
    """
    Collects and analyzes pipeline failures.
    """

    def __init__(self):

        self.failures: List[FailureRecord] = []

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def add_failure(
        self,
        stage: str,
        error_type: str,
        message: str,
        document_id: str | None = None,
        image_id: str | None = None,
        file_path: str | None = None,
    ) -> None:
        """
        Record a pipeline failure.
        """

        record = FailureRecord(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            stage=stage,
            error_type=error_type,
            message=message,
            document_id=document_id,
            image_id=image_id,
            file_path=file_path,
        )

        self.failures.append(record)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def total_failures(self) -> int:
        return len(self.failures)

    def failures_by_stage(self) -> Dict[str, int]:

        counts: Dict[str, int] = {}

        for failure in self.failures:
            counts[failure.stage] = counts.get(failure.stage, 0) + 1

        return counts

    def failures_by_type(self) -> Dict[str, int]:

        counts: Dict[str, int] = {}

        for failure in self.failures:
            counts[failure.error_type] = (
                counts.get(failure.error_type, 0) + 1
            )

        return counts

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_dataframe(self) -> pd.DataFrame:

        if not self.failures:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "stage",
                    "error_type",
                    "message",
                    "document_id",
                    "image_id",
                    "file_path",
                ]
            )

        return pd.DataFrame(
            [asdict(record) for record in self.failures]
        )

    def save_csv(
        self,
        filename: str = "failure_report.csv",
    ) -> Path:
        """
        Save all failures as CSV.
        """

        output = REPORTS_DIR / filename

        self.to_dataframe().to_csv(
            output,
            index=False,
        )

        return output

    # ---------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------

    def summary(self) -> str:

        lines = [
            "",
            "Failure Analysis",
            "-" * 40,
            f"Total Failures : {self.total_failures()}",
            "",
            "By Stage",
        ]

        for stage, count in self.failures_by_stage().items():
            lines.append(f"  {stage:<20}{count}")

        lines.append("")
        lines.append("By Error Type")

        for error, count in self.failures_by_type().items():
            lines.append(f"  {error:<20}{count}")

        return "\n".join(lines)