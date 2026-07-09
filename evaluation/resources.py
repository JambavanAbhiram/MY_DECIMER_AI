"""
evaluation/resources.py

Utilities for monitoring CPU, RAM, and GPU resource
usage during pipeline execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
import psutil

from evaluation.config import REPORTS_DIR

# GPU monitoring is optional
try:
    import GPUtil

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class ResourceMonitor:
    """
    Monitors CPU, RAM and GPU usage.
    """

    def __init__(self):

        self.cpu_usage: List[float] = []
        self.ram_usage: List[float] = []

        self.gpu_usage: List[float] = []
        self.gpu_memory: List[float] = []

    # ---------------------------------------------------------
    # Sampling
    # ---------------------------------------------------------

    def sample(self):
        """
        Record a single resource snapshot.
        """

        # CPU (%)
        self.cpu_usage.append(
            psutil.cpu_percent(interval=None)
        )

        # RAM (MB)
        ram = psutil.Process().memory_info().rss / (1024 ** 2)

        self.ram_usage.append(ram)

        # GPU
        if GPU_AVAILABLE:

            gpus = GPUtil.getGPUs()

            if gpus:

                gpu = gpus[0]

                self.gpu_usage.append(
                    gpu.load * 100
                )

                self.gpu_memory.append(
                    gpu.memoryUsed
                )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self):

        stats = {

            "cpu_average_percent":
                round(sum(self.cpu_usage) / len(self.cpu_usage), 2)
                if self.cpu_usage else 0,

            "cpu_peak_percent":
                round(max(self.cpu_usage), 2)
                if self.cpu_usage else 0,

            "ram_average_mb":
                round(sum(self.ram_usage) / len(self.ram_usage), 2)
                if self.ram_usage else 0,

            "ram_peak_mb":
                round(max(self.ram_usage), 2)
                if self.ram_usage else 0,
        }

        if GPU_AVAILABLE and self.gpu_usage:

            stats["gpu_average_percent"] = round(
                sum(self.gpu_usage) / len(self.gpu_usage),
                2,
            )

            stats["gpu_peak_percent"] = round(
                max(self.gpu_usage),
                2,
            )

            stats["gpu_peak_memory_mb"] = round(
                max(self.gpu_memory),
                2,
            )

        return stats

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_dataframe(self):

        stats = self.statistics()

        return pd.DataFrame(
            [
                {
                    "metric": k,
                    "value": v,
                }
                for k, v in stats.items()
            ]
        )

    def save_csv(
        self,
        filename="resource_report.csv",
    ) -> Path:

        output = REPORTS_DIR / filename

        self.to_dataframe().to_csv(
            output,
            index=False,
        )

        return output

    # ---------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------

    def summary(self):

        stats = self.statistics()

        lines = [
            "",
            "Resource Usage Summary",
            "-" * 40,
        ]

        for key, value in stats.items():

            lines.append(
                f"{key:<30}{value}"
            )

        return "\n".join(lines)