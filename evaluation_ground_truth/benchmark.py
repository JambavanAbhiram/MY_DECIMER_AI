"""
benchmark.py

Main entry point for the DECIMER Ground Truth Evaluation.

Workflow
--------
1. Ask user for:
   - Ground Truth Excel
   - Pipeline metadata.csv
   - Output directory

2. Validate inputs.

3. Evaluate predictions.

4. Generate:
   - evaluation_summary.json
   - evaluation_details.csv
   - evaluation_report.html
"""

from pathlib import Path
import pandas as pd

from evaluation_ground_truth.recognizer_eval import evaluate
from evaluation_ground_truth.report import write_report


# =============================================================================
# Input Helpers
# =============================================================================

def get_existing_file(prompt: str) -> Path:
    while True:

        path = Path(input(prompt).strip().strip('"'))

        if path.exists() and path.is_file():
            return path

        print("\n❌ File not found.")
        print("Please enter a valid file path.\n")


def get_output_directory(prompt: str) -> Path:

    path = Path(input(prompt).strip().strip('"'))

    path.mkdir(parents=True, exist_ok=True)

    return path


# =============================================================================
# Metadata Validation
# =============================================================================

def validate_metadata_file(metadata_path: Path):
    """
    Ensures the selected CSV is the recognition metadata
    and not document_inventory.csv or another CSV.
    """

    try:
        df = pd.read_csv(metadata_path, nrows=5)

    except Exception as e:
        raise ValueError(
            f"\nUnable to read metadata file.\n{e}"
        )

    required = {
        "image_id",
        "smiles",
        "processing_status"
    }

    missing = required - set(df.columns)

    if missing:

        print("\n❌ Invalid metadata file selected.\n")

        print("Missing required columns:")

        for col in sorted(missing):
            print(f"   • {col}")

        print("\nExpected a recognition metadata CSV.")

        print("\nYou probably selected one of these instead:")

        print("   • document_inventory.csv")
        print("   • master_database.csv")
        print("   • inventory.csv")

        raise SystemExit(1)


# =============================================================================
# Main
# =============================================================================

def main():

    print("=" * 70)
    print("        DECIMER Ground Truth Evaluation")
    print("=" * 70)

    print("\nEnter the requested paths.\n")

    gt_path = get_existing_file(
        "Ground Truth Excel (.xlsx):\n> "
    )

    metadata_path = get_existing_file(
        "\nPipeline metadata.csv:\n> "
    )

    output_dir = get_output_directory(
        "\nEvaluation Output Folder:\n> "
    )

    print("\nValidating metadata file...")

    validate_metadata_file(metadata_path)

    print("✓ Metadata file looks valid.\n")

    print("Running evaluation...\n")

    details, summary = evaluate(
        gt_path=gt_path,
        metadata_path=metadata_path
    )

    write_report(
        summary=summary,
        details=details,
        output_dir=output_dir
    )

    print("=" * 70)
    print("Evaluation Completed Successfully")
    print("=" * 70)

    print(f"""
Total Formula Images : {summary['total_formula_images']}
Recognized           : {summary['recognized']}
Recognition Failed   : {summary['recognition_failed']}
Missing Predictions  : {summary['missing']}
Invalid SMILES       : {summary['invalid_smiles']}

Recognition Rate     : {summary['recognition_rate']} %
Canonical Accuracy   : {summary['overall_accuracy']} %
Exact Accuracy       : {summary['exact_accuracy']} %
""")

    print("\nReports saved to:")

    print(output_dir.resolve())

    print("\nGenerated Files")

    print("  • evaluation_summary.json")
    print("  • evaluation_details.csv")
    print("  • evaluation_report.html")


if __name__ == "__main__":
    main()