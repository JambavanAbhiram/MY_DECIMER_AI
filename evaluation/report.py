"""
evaluation/report.py

Generates evaluation reports from all pipeline evaluators.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from evaluation.config import REPORTS_DIR


class ReportGenerator:
    """
    Combines all evaluation results into a single report.
    """

    def __init__(self):

        self.sections: Dict[str, Any] = {}

    # ---------------------------------------------------------
    # Add Section
    # ---------------------------------------------------------

    def add_section(
        self,
        name: str,
        results: Any,
    ) -> None:
        """
        Add evaluator results.

        Supports:
        - dict
        - list of dicts
        - DataFrame
        """

        self.sections[name] = results

    # ---------------------------------------------------------
    # Summary DataFrame
    # ---------------------------------------------------------

    def summary_dataframe(self):

        rows = []

        for section, metrics in self.sections.items():

            # -----------------------------
            # Dictionary
            # -----------------------------
            if isinstance(metrics, dict):

                for metric, value in metrics.items():

                    rows.append(
                        {
                            "section": section,
                            "metric": metric,
                            "value": value,
                        }
                    )

            # -----------------------------
            # List (usually list of dicts)
            # -----------------------------
            elif isinstance(metrics, list):

                for item in metrics:

                    if isinstance(item, dict):

                        row = {"section": section}
                        row.update(item)
                        rows.append(row)

                    else:

                        rows.append(
                            {
                                "section": section,
                                "metric": "",
                                "value": item,
                            }
                        )

            # -----------------------------
            # DataFrame
            # -----------------------------
            elif isinstance(metrics, pd.DataFrame):

                df = metrics.copy()
                df.insert(0, "section", section)
                rows.extend(df.to_dict(orient="records"))

            # -----------------------------
            # Anything else
            # -----------------------------
            else:

                rows.append(
                    {
                        "section": section,
                        "metric": "",
                        "value": metrics,
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
                default=str,
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

            # Dictionary
            if isinstance(metrics, dict):

                for metric, value in metrics.items():

                    lines.append(
                        f"{metric:<35}{value}"
                    )

            # List
            elif isinstance(metrics, list):

                for item in metrics:

                    lines.append(str(item))

            # DataFrame
            elif isinstance(metrics, pd.DataFrame):

                lines.append(metrics.to_string(index=False))

            else:

                lines.append(str(metrics))

        return "\n".join(lines)