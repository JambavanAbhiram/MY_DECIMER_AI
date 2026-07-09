"""
evaluation/runtime.py

Utilities for measuring and reporting execution times of
pipeline stages.

This module is independent of the processing pipeline and can
be reused by both the pipeline and the evaluation framework.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List

import pandas as pd

from evaluation.config import REPORTS_DIR


class RuntimeTracker:
    """
    Tracks execution times for pipeline stages.
    """

    def __init__(self) -> None:
        self._start_times: Dict[str, float] = {}
        self._durations: Dict[str, List[float]] = {}

    # ---------------------------------------------------------
    # Timing
    # ---------------------------------------------------------

    def start(self, stage: str) -> None:
        """
        Start timing a stage.

        Parameters
        ----------
        stage : str
            Name of the pipeline stage.
        """
        self._start_times[stage] = time.perf_counter()

    def stop(self, stage: str) -> float:
        """
        Stop timing a stage.

        Returns
        -------
        float
            Duration in seconds.
        """
        if stage not in self._start_times:
            raise RuntimeError(f"Stage '{stage}' was never started.")

        duration = time.perf_counter() - self._start_times.pop(stage)

        self._durations.setdefault(stage, []).append(duration)

        return duration

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def total_runtime(self) -> float:
        """
        Total runtime across all stages.
        """
        return sum(sum(values) for values in self._durations.values())

    def average_runtime(self, stage: str) -> float:
        """
        Average runtime for a stage.
        """
        values = self._durations.get(stage, [])

        if not values:
            return 0.0

        return sum(values) / len(values)

    def stage_runtime(self, stage: str) -> float:
        """
        Total runtime for a single stage.
        """
        return sum(self._durations.get(stage, []))

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert runtime information to a DataFrame.
        """

        rows = []

        for stage, values in self._durations.items():
            rows.append(
                {
                    "stage": stage,
                    "runs": len(values),
                    "total_seconds": sum(values),
                    "average_seconds": sum(values) / len(values),
                    "min_seconds": min(values),
                    "max_seconds": max(values),
                }
            )

        return pd.DataFrame(rows)

    def save_csv(
        self,
        filename: str = "runtime_report.csv",
    ) -> Path:
        """
        Save runtime report.
        """

        output = REPORTS_DIR / filename

        self.to_dataframe().to_csv(
            output,
            index=False,
        )

        return output

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summary(self) -> str:
        """
        Human-readable summary.
        """

        lines = [
            "",
            "Runtime Summary",
            "-" * 40,
        ]

        for stage in sorted(self._durations):

            lines.append(
                f"{stage:<20}"
                f"{self.stage_runtime(stage):8.3f} s"
            )

        lines.append("-" * 40)

        lines.append(
            f"{'TOTAL':<20}"
            f"{self.total_runtime():8.3f} s"
        )

        return "\n".join(lines)