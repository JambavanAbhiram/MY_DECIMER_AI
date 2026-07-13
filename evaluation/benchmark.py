"""
evaluation/benchmark.py

Runs the complete evaluation pipeline.

This module orchestrates all evaluation components and generates
a consolidated benchmark report.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from evaluation.inventory_eval import InventoryEvaluator
from evaluation.renderer_eval import RendererEvaluator
from evaluation.segmentation_eval import SegmentationEvaluator
from evaluation.cleaner_eval import CleanerEvaluator
from evaluation.recognizer_eval import RecognizerEvaluator
from evaluation.metadata_eval import MetadataEvaluator

from evaluation.runtime import RuntimeTracker
from evaluation.resources import ResourceMonitor
from evaluation.failure_analysis import FailureAnalyzer
from evaluation.report import ReportGenerator


class Benchmark:
    """
    Runs the complete evaluation framework.
    """

    def __init__(
        self,
        inventory_csv: str | Path,
        metadata_csv: str | Path,
    ):

        self.inventory_csv = Path(inventory_csv)
        self.metadata_csv = Path(metadata_csv)

        self.runtime = RuntimeTracker()
        self.resources = ResourceMonitor()
        self.failures = FailureAnalyzer()
        self.report = ReportGenerator()

    # ---------------------------------------------------------
    # Inventory
    # ---------------------------------------------------------

    def evaluate_inventory(self):

        self.runtime.start("inventory")

        evaluator = InventoryEvaluator(
            self.inventory_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("inventory")

        self.resources.sample()

        self.report.add_section(
            "inventory",
            results,
        )

    # ---------------------------------------------------------
    # Renderer
    # ---------------------------------------------------------

    def evaluate_renderer(self):

        self.runtime.start("renderer")

        evaluator = RendererEvaluator(
            self.metadata_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("renderer")

        self.resources.sample()

        self.report.add_section(
            "renderer",
            results,
        )

    # ---------------------------------------------------------
    # Segmentation
    # ---------------------------------------------------------

    def evaluate_segmentation(self):

        self.runtime.start("segmentation")

        evaluator = SegmentationEvaluator(
            self.metadata_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("segmentation")

        self.resources.sample()

        self.report.add_section(
            "segmentation",
            results,
        )

    # ---------------------------------------------------------
    # Cleaner
    # ---------------------------------------------------------

    def evaluate_cleaner(self):

        self.runtime.start("cleaner")

        evaluator = CleanerEvaluator(
            self.metadata_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("cleaner")

        self.resources.sample()

        self.report.add_section(
            "cleaner",
            results,
        )

    # ---------------------------------------------------------
    # Recognition
    # ---------------------------------------------------------

    def evaluate_recognizer(self):

        self.runtime.start("recognizer")

        evaluator = RecognizerEvaluator(
            self.metadata_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("recognizer")

        self.resources.sample()

        self.report.add_section(
            "recognizer",
            results,
        )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    def evaluate_metadata(self):

        self.runtime.start("metadata")

        evaluator = MetadataEvaluator(
            self.metadata_csv
        )

        results = evaluator.evaluate()

        self.runtime.stop("metadata")

        self.resources.sample()

        self.report.add_section(
            "metadata",
            results,
        )

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    def evaluate_runtime(self):

        runtime_df = self.runtime.to_dataframe()

        self.runtime.save_csv()

        self.report.add_section(
            "runtime",
            runtime_df.to_dict(orient="records"),
        )

    # ---------------------------------------------------------
    # Resources
    # ---------------------------------------------------------

    def evaluate_resources(self):

        resource_df = self.resources.to_dataframe()

        self.resources.save_csv()

        self.report.add_section(
            "resources",
            resource_df.to_dict(orient="records"),
        )

    # ---------------------------------------------------------
    # Failures
    # ---------------------------------------------------------

    def evaluate_failures(self):

        self.failures.save_csv()

        self.report.add_section(
            "failures",
            {
                "total_failures":
                self.failures.total_failures()
            },
        )

    # ---------------------------------------------------------
    # Run Benchmark
    # ---------------------------------------------------------

    def run(self):

        self.evaluate_inventory()

        self.evaluate_renderer()

        self.evaluate_segmentation()

        self.evaluate_cleaner()

        self.evaluate_recognizer()

        self.evaluate_metadata()

        self.evaluate_runtime()

        self.evaluate_resources()

        self.evaluate_failures()

        self.report.save_csv()

        self.report.save_json()

        print(self.report.summary())

        return self.report.summary_dataframe()
    
if __name__ == "__main__":

    benchmark = Benchmark(
        inventory_csv="data/master_inventory.csv",
        metadata_csv="data/master_metadata.csv",
    )

    benchmark.run()