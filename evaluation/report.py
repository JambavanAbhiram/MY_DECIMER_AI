"""
evaluation/report.py

Generates evaluation reports from all pipeline evaluators.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pandas as pd

from evaluation.config import REPORTS_DIR


class ReportGenerator:
    """
    Combines all evaluation results into a single report.
    """

    def __init__(self):

        self.sections: Dict[str, Dict] = {}

    # ---------------------------------------------------------
    # Add Section
    # ---------------------------------------------------------

    def add_section(
        self,
        name: str,
        results: Dict,
    ) -> None:
        """
        Add evaluator results.

        Example
        -------
        add_section("inventory", inventory_results)
        """

        self.sections[name] = results

    # ---------------------------------------------------------
    # Summary DataFrame
    # ---------------------------------------------------------

    def summary_dataframe(self):

        rows = []

        for section, metrics in self.sections.items():

            for metric, value in metrics.items():

                rows.append(
                    {
                        "section": section,
                        "metric": metric,
                        "value": value,
                    }
                )

        return pd.DataFrame(rows)

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------

    def save_csv(
        self,
        filename="benchmark_summary.csv",
    ) -> Path:

        output = REPORTS_DIR / filename

        self.summary_dataframe().to_csv(
            output,
            index=False,
        )

        return output

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    def save_json(
        self,
        filename="benchmark_summary.json",
    ) -> Path:

        output = REPORTS_DIR / filename

        with open(
            output,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                self.sections,
                fp,
                indent=4,
            )

        return output

    # ---------------------------------------------------------
    # Console Summary
    # ---------------------------------------------------------

    def summary(self):

        lines = []

        lines.append("")
        lines.append("=" * 60)
        lines.append("PIPELINE EVALUATION REPORT")
        lines.append("=" * 60)

        for section, metrics in self.sections.items():

            lines.append("")
            lines.append(section.upper())
            lines.append("-" * 60)

            for metric, value in metrics.items():

                lines.append(
                    f"{metric:<35}{value}"
                )

        return "\n".join(lines)