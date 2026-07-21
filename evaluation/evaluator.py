"""
evaluator.py

Unified evaluation framework for the DECIMER pipeline.

This module replaces:
    • inventory_eval.py
    • renderer_eval.py
    • segmentation_eval.py
    • cleaner_eval.py
    • recognizer_eval.py
    • metadata_eval.py
    • benchmark.py

Author:
    DECIMER Project
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, List

import json
import time

import cv2
import pandas as pd
import numpy as np

from rdkit import Chem


class EvaluationPipeline:
    """
    Unified evaluator for the entire DECIMER pipeline.

    All evaluation results are stored in:

        self.summary
        self.failures
        self.details
    """

    # ---------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------

    def __init__(
        self,
        inventory_csv: str | Path,
        metadata_csv: str | Path,
        ground_truth_excel: str | Path | None = None,
        output_dir: str | Path = "evaluation_results",
    ):

        self.inventory_csv = Path(inventory_csv)
        self.metadata_csv = Path(metadata_csv)

        self.ground_truth_excel = (
            Path(ground_truth_excel)
            if ground_truth_excel
            else None
        )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.inventory = None
        self.metadata = None
        self.ground_truth = None

        self.summary: Dict[str, object] = {}

        self.details: List[Dict] = []

        self.failures: List[Dict] = []

        self.start_time = None
        self.end_time = None

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    def start(self):

        self.start_time = time.perf_counter()

    def stop(self):

        self.end_time = time.perf_counter()

        self.summary["runtime_seconds"] = round(
            self.end_time - self.start_time,
            3,
        )

    # ---------------------------------------------------------
    # Failure Logging
    # ---------------------------------------------------------

    def add_failure(
        self,
        stage,
        message,
        image_id=None,
        file_path=None,
    ):

        self.failures.append(
            {
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "stage": stage,
                "image_id": image_id,
                "file_path": file_path,
                "message": message,
            }
        )

    # ---------------------------------------------------------
    # Load Files
    # ---------------------------------------------------------

    def load_inputs(self):

        if not self.inventory_csv.exists():
            raise FileNotFoundError(
                self.inventory_csv
            )

        if not self.metadata_csv.exists():
            raise FileNotFoundError(
                self.metadata_csv
            )

        self.inventory = pd.read_csv(
            self.inventory_csv
        )

        self.metadata = pd.read_csv(
            self.metadata_csv
        )

        if self.ground_truth_excel:

            self.ground_truth = pd.read_excel(
                self.ground_truth_excel
            )

    # ---------------------------------------------------------
    # Required Columns
    # ---------------------------------------------------------

    @staticmethod
    def validate_columns(
        dataframe,
        required_columns,
        dataframe_name,
    ):

        missing = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                f"\n{dataframe_name} is missing columns:\n"
                + "\n".join(missing)
            )

    # ---------------------------------------------------------
    # RDKit Helper
    # ---------------------------------------------------------

    @staticmethod
    def canonicalize(smiles):

        if pd.isna(smiles):
            return None

        smiles = str(smiles).strip()

        if smiles == "":
            return None

        try:

            molecule = Chem.MolFromSmiles(smiles)

            if molecule is None:
                return None

            return Chem.MolToSmiles(
                molecule,
                canonical=True,
            )

        except Exception:

            return None

    # ---------------------------------------------------------
    # Save Helper
    # ---------------------------------------------------------

    def save_dataframe(
        self,
        dataframe,
        filename,
    ):

        dataframe.to_csv(
            self.output_dir / filename,
            index=False,
        )

    def save_json(
        self,
        data,
        filename,
    ):

        with open(
            self.output_dir / filename,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                data,
                fp,
                indent=4,
                default=str,
            )
    # =========================================================
    # Inventory Evaluation
    # =========================================================

    def evaluate_inventory(self):

        print("Evaluating Inventory...")

        required = [
            "document_id",
            "pdf_name",
            "pdf_path",
            "processed",
        ]

        self.validate_columns(
            self.inventory,
            required,
            "Inventory",
        )

        results = {}

        results["total_documents"] = len(self.inventory)

        results["processed_documents"] = int(
            self.inventory["processed"].sum()
        )

        results["unprocessed_documents"] = (
            results["total_documents"]
            - results["processed_documents"]
        )

        results["duplicate_document_ids"] = int(
            self.inventory["document_id"]
            .duplicated()
            .sum()
        )

        missing_files = 0
        empty_files = 0

        for pdf in self.inventory["pdf_path"]:

            path = Path(pdf)

            if not path.exists():
                missing_files += 1
                self.add_failure(
                    "Inventory",
                    "Missing PDF",
                    file_path=pdf,
                )
                continue

            if path.stat().st_size == 0:
                empty_files += 1

        results["missing_pdf_files"] = missing_files
        results["empty_pdf_files"] = empty_files

        self.summary["inventory"] = results

    # =========================================================
    # Rendering Evaluation
    # =========================================================

    def evaluate_rendering(self):

        print("Evaluating Rendered Pages...")

        required = [
            "page_number",
            "image_path",
        ]

        self.validate_columns(
            self.metadata,
            required,
            "Metadata",
        )

        results = {}

        unreadable = 0
        blank = 0
        missing = 0

        widths = []
        heights = []

        for image_path in self.metadata["image_path"]:

            path = Path(image_path)

            if not path.exists():

                missing += 1

                self.add_failure(
                    "Renderer",
                    "Missing rendered image",
                    file_path=image_path,
                )

                continue

            image = cv2.imread(str(path))

            if image is None:

                unreadable += 1

                self.add_failure(
                    "Renderer",
                    "Unreadable rendered image",
                    file_path=image_path,
                )

                continue

            h, w = image.shape[:2]

            widths.append(w)
            heights.append(h)

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )

            if np.std(gray) < 2:
                blank += 1

        results["rendered_pages"] = len(
            self.metadata
        )

        results["missing_images"] = missing

        results["unreadable_images"] = unreadable

        results["blank_images"] = blank

        if widths:

            results["average_width"] = round(
                float(np.mean(widths)),
                2,
            )

            results["average_height"] = round(
                float(np.mean(heights)),
                2,
            )

        self.summary["renderer"] = results

    # =========================================================
    # Segmentation Evaluation
    # =========================================================

    def evaluate_segmentation(self):

        print("Evaluating Segmentation...")

        required = [
            "image_id",
            "image_path",
        ]

        self.validate_columns(
            self.metadata,
            required,
            "Metadata",
        )

        results = {}

        duplicate_ids = int(
            self.metadata["image_id"]
            .duplicated()
            .sum()
        )

        invalid_images = 0

        for _, row in self.metadata.iterrows():

            path = Path(row["image_path"])

            if not path.exists():
                continue

            image = cv2.imread(str(path))

            if image is None:
                invalid_images += 1
                continue

            h, w = image.shape[:2]

            if h <= 0 or w <= 0:
                invalid_images += 1

        results["segmented_structures"] = len(
            self.metadata
        )

        results["duplicate_image_ids"] = duplicate_ids

        results["invalid_segment_images"] = invalid_images

        self.summary["segmentation"] = results

    # =========================================================
    # Cleaner Evaluation
    # =========================================================

    def evaluate_cleaner(self):

        print("Evaluating Cleaned Images...")

        if "clean_image_path" not in self.metadata.columns:

            self.summary["cleaner"] = {
                "status": "Skipped",
                "reason": "clean_image_path column missing",
            }

            return

        results = {}

        unreadable = 0
        missing = 0
        empty = 0

        widths = []
        heights = []

        for clean_path in self.metadata["clean_image_path"]:

            if pd.isna(clean_path):
                continue

            path = Path(clean_path)

            if not path.exists():

                missing += 1

                self.add_failure(
                    "Cleaner",
                    "Missing cleaned image",
                    file_path=clean_path,
                )

                continue

            if path.stat().st_size == 0:
                empty += 1

            image = cv2.imread(str(path))

            if image is None:
                unreadable += 1
                continue

            h, w = image.shape[:2]

            widths.append(w)
            heights.append(h)

        results["cleaned_images"] = len(
            self.metadata
        )

        results["missing_clean_images"] = missing

        results["empty_clean_images"] = empty

        results["unreadable_clean_images"] = unreadable

        if widths:

            results["average_width"] = round(
                float(np.mean(widths)),
                2,
            )

            results["average_height"] = round(
                float(np.mean(heights)),
                2,
            )

        self.summary["cleaner"] = results

    # =========================================================
    # Recognition Evaluation
    # =========================================================

    def evaluate_recognition(self):

        print("Evaluating Recognition...")

        required = [
            "image_id",
            "smiles",
        ]

        self.validate_columns(
            self.metadata,
            required,
            "Metadata",
        )

        results = {}

        total = len(self.metadata)

        missing = 0
        invalid = 0
        valid = 0
        duplicates = 0

        canonical_smiles = []

        for _, row in self.metadata.iterrows():

            image_id = row["image_id"]
            smiles = row["smiles"]

            if pd.isna(smiles) or str(smiles).strip() == "":

                missing += 1

                self.add_failure(
                    stage="Recognition",
                    message="Missing SMILES",
                    image_id=image_id,
                )

                continue

            canonical = self.canonicalize(smiles)

            if canonical is None:

                invalid += 1

                self.add_failure(
                    stage="Recognition",
                    message="Invalid SMILES",
                    image_id=image_id,
                )

            else:

                valid += 1
                canonical_smiles.append(canonical)

        duplicates = pd.Series(
            canonical_smiles
        ).duplicated().sum()

        results["total_predictions"] = total
        results["valid_smiles"] = valid
        results["invalid_smiles"] = invalid
        results["missing_predictions"] = missing
        results["duplicate_predictions"] = int(duplicates)

        if total:

            results["recognition_success_rate"] = round(
                valid / total * 100,
                2,
            )

        else:

            results["recognition_success_rate"] = 0.0

        self.summary["recognition"] = results

    # =========================================================
    # Metadata Evaluation
    # =========================================================

    def evaluate_metadata(self):

        print("Evaluating Metadata...")

        required = [
            "document_id",
            "page_number",
            "image_id",
            "image_path",
        ]

        self.validate_columns(
            self.metadata,
            required,
            "Metadata",
        )

        results = {}

        results["total_records"] = len(
            self.metadata
        )

        results["duplicate_image_ids"] = int(
            self.metadata["image_id"]
            .duplicated()
            .sum()
        )

        results["duplicate_document_ids"] = int(
            self.metadata["document_id"]
            .duplicated()
            .sum()
        )

        missing_paths = int(
            self.metadata["image_path"]
            .isna()
            .sum()
        )

        results["missing_image_paths"] = missing_paths

        invalid_pages = int(
            (
                self.metadata["page_number"] < 1
            ).sum()
        )

        results["invalid_page_numbers"] = invalid_pages

        complete_rows = self.metadata.dropna().shape[0]

        if len(self.metadata):

            completeness = (
                complete_rows
                / len(self.metadata)
                * 100
            )

        else:

            completeness = 0

        results["complete_records"] = complete_rows

        results["metadata_completeness"] = round(
            completeness,
            2,
        )

        self.summary["metadata"] = results

    # =========================================================
    # Ground Truth Evaluation
    # =========================================================

    def evaluate_ground_truth(self):

        if self.ground_truth is None:

            self.summary["ground_truth"] = {
                "status": "Skipped",
                "reason": "Ground truth not provided",
            }

            return

        print("Evaluating Ground Truth...")

        required_gt = [
            "image_id",
            "ground_truth_smiles",
        ]

        self.validate_columns(
            self.ground_truth,
            required_gt,
            "Ground Truth",
        )

        prediction_df = self.metadata.copy()

        prediction_df["predicted_canonical"] = (
            prediction_df["smiles"]
            .apply(self.canonicalize)
        )

        gt_df = self.ground_truth.copy()

        gt_df["ground_truth_canonical"] = (
            gt_df["ground_truth_smiles"]
            .apply(self.canonicalize)
        )

        merged = gt_df.merge(
            prediction_df[
                [
                    "image_id",
                    "smiles",
                    "predicted_canonical",
                ]
            ],
            on="image_id",
            how="left",
        )

        merged["exact_match"] = (
            merged["ground_truth_smiles"]
            .fillna("")
            .astype(str)
            .str.strip()
            ==
            merged["smiles"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        merged["canonical_match"] = (
            merged["ground_truth_canonical"]
            ==
            merged["predicted_canonical"]
        )

        total = len(merged)

        exact = int(
            merged["exact_match"].sum()
        )

        canonical = int(
            merged["canonical_match"].sum()
        )

        missing = int(
            merged["smiles"].isna().sum()
        )

        results = {}

        results["ground_truth_images"] = total
        results["exact_matches"] = exact
        results["canonical_matches"] = canonical
        results["missing_predictions"] = missing

        if total:

            results["exact_accuracy"] = round(
                exact / total * 100,
                2,
            )

            results["canonical_accuracy"] = round(
                canonical / total * 100,
                2,
            )

        else:

            results["exact_accuracy"] = 0.0
            results["canonical_accuracy"] = 0.0

        self.details = merged

        self.summary["ground_truth"] = results

    # =========================================================
    # Failure Summary
    # =========================================================

    def summarize_failures(self):

        print("Summarizing Failures...")

        results = {}

        results["total_failures"] = len(self.failures)

        stage_counts = {}

        for failure in self.failures:

            stage = failure["stage"]

            stage_counts[stage] = (
                stage_counts.get(stage, 0) + 1
            )

        results["failures_by_stage"] = stage_counts

        self.summary["failures"] = results

    # =========================================================
    # Overall Summary
    # =========================================================

    def generate_summary(self):

        print("Generating Overall Summary...")

        inventory = self.summary.get("inventory", {})
        recognition = self.summary.get("recognition", {})
        metadata = self.summary.get("metadata", {})
        ground_truth = self.summary.get("ground_truth", {})

        overall = {}

        overall["documents_processed"] = inventory.get(
            "processed_documents",
            0,
        )

        overall["total_predictions"] = recognition.get(
            "total_predictions",
            0,
        )

        overall["valid_smiles"] = recognition.get(
            "valid_smiles",
            0,
        )

        overall["invalid_smiles"] = recognition.get(
            "invalid_smiles",
            0,
        )

        overall["metadata_completeness"] = metadata.get(
            "metadata_completeness",
            0,
        )

        if (
            isinstance(ground_truth, dict)
            and "canonical_accuracy" in ground_truth
        ):

            overall["canonical_accuracy"] = ground_truth[
                "canonical_accuracy"
            ]

            overall["exact_accuracy"] = ground_truth[
                "exact_accuracy"
            ]

        self.summary["overall"] = overall

    # =========================================================
    # Export Reports
    # =========================================================

    def export_reports(self):

        print("Exporting Reports...")

        # ------------------------------------------
        # Summary JSON
        # ------------------------------------------

        self.save_json(
            self.summary,
            "evaluation_summary.json",
        )

        # ------------------------------------------
        # Failure CSV
        # ------------------------------------------

        failure_df = pd.DataFrame(
            self.failures
        )

        self.save_dataframe(
            failure_df,
            "evaluation_failures.csv",
        )

        # ------------------------------------------
        # Ground Truth Details
        # ------------------------------------------

        if isinstance(
            self.details,
            pd.DataFrame,
        ):

            self.save_dataframe(
                self.details,
                "evaluation_details.csv",
            )

        # ------------------------------------------
        # Summary Table
        # ------------------------------------------

        rows = []

        for section, values in self.summary.items():

            if not isinstance(values, dict):
                continue

            for metric, value in values.items():

                rows.append(
                    {
                        "section": section,
                        "metric": metric,
                        "value": value,
                    }
                )

        summary_df = pd.DataFrame(rows)

        self.save_dataframe(
            summary_df,
            "evaluation_summary.csv",
        )

    # =========================================================
    # HTML Report
    # =========================================================

    def export_html_report(self):

        print("Generating HTML Report...")

        html = f"""
<!DOCTYPE html>

<html>

<head>

<title>DECIMER Evaluation Report</title>

<style>

body {{
    font-family: Arial;
    margin: 40px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th {{
    background: #2c3e50;
    color: white;
    padding: 10px;
}}

td {{
    border: 1px solid #cccccc;
    padding: 8px;
}}

tr:nth-child(even) {{
    background: #f5f5f5;
}}

h1 {{
    color: #2c3e50;
}}

h2 {{
    margin-top: 35px;
}}

</style>

</head>

<body>

<h1>DECIMER Pipeline Evaluation Report</h1>

<p>
Generated:
{datetime.now().strftime("%d %B %Y %H:%M:%S")}
</p>

"""

        for section, metrics in self.summary.items():

            html += f"<h2>{section.title()}</h2>"

            html += """
<table>
<tr>
<th>Metric</th>
<th>Value</th>
</tr>
"""

            if isinstance(metrics, dict):

                for key, value in metrics.items():

                    html += (
                        "<tr>"
                        f"<td>{key}</td>"
                        f"<td>{value}</td>"
                        "</tr>"
                    )

            html += "</table>"

        html += """

</body>

</html>

"""

        with open(
            self.output_dir / "evaluation_report.html",
            "w",
            encoding="utf-8",
        ) as fp:

            fp.write(html)

    # =========================================================
    # Run Complete Evaluation
    # =========================================================

    def run(self):

        print("=" * 70)
        print("DECIMER Pipeline Evaluation")
        print("=" * 70)

        self.start()

        # -------------------------------
        # Load Inputs
        # -------------------------------

        self.load_inputs()

        # -------------------------------
        # Stage Evaluations
        # -------------------------------

        self.evaluate_inventory()

        self.evaluate_rendering()

        self.evaluate_segmentation()

        self.evaluate_cleaner()

        self.evaluate_recognition()

        self.evaluate_metadata()

        self.evaluate_ground_truth()

        # -------------------------------
        # Final Reports
        # -------------------------------

        self.summarize_failures()

        self.stop()

        self.generate_summary()

        self.export_reports()

        self.export_html_report()

        # -------------------------------
        # Console Summary
        # -------------------------------

        print("\n")
        print("=" * 70)
        print("Evaluation Completed Successfully")
        print("=" * 70)

        print(f"\nOutput Folder : {self.output_dir.resolve()}")

        print("\nGenerated Files")
        print("-" * 70)

        print("✓ evaluation_summary.json")
        print("✓ evaluation_summary.csv")
        print("✓ evaluation_details.csv")
        print("✓ evaluation_failures.csv")
        print("✓ evaluation_report.html")

        print("\nOverall Summary")
        print("-" * 70)

        overall = self.summary.get("overall", {})

        for key, value in overall.items():

            print(f"{key:<35}{value}")

        print(
            f"\nTotal Runtime : "
            f"{self.summary.get('runtime_seconds',0)} seconds"
        )

        print("=" * 70)

        return self.summary


# =========================================================
# Interactive Helpers
# =========================================================

def get_existing_file(prompt: str) -> Path:

    while True:

        path = Path(
            input(prompt).strip().strip('"')
        )

        if path.exists():
            return path

        print("\nFile not found.\n")


def get_output_folder(prompt: str) -> Path:

    path = Path(
        input(prompt).strip().strip('"')
    )

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)
    print("DECIMER Unified Evaluation Framework")
    print("=" * 70)

    inventory = get_existing_file(
        "\nInventory CSV\n> "
    )

    metadata = get_existing_file(
        "\nMetadata CSV\n> "
    )

    answer = input(
        "\nDo you have Ground Truth? (y/n)\n> "
    ).strip().lower()

    ground_truth = None

    if answer == "y":

        ground_truth = get_existing_file(
            "\nGround Truth Excel\n> "
        )

    output = get_output_folder(
        "\nOutput Folder\n> "
    )

    evaluator = EvaluationPipeline(
        inventory_csv=inventory,
        metadata_csv=metadata,
        ground_truth_excel=ground_truth,
        output_dir=output,
    )

    evaluator.run()


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    main()