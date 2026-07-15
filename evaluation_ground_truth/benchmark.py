"""
benchmark.py

Main entry point for the DECIMER Ground Truth Evaluation.

Workflow
--------
1. Ask user for:
   - Ground Truth Excel
   - Pipeline metadata.csv
   - Output directory

2. Evaluate predictions against the ground truth.

3. Generate:
   - evaluation_summary.json
   - evaluation_details.csv
   - evaluation_report.html
"""

from pathlib import Path

from evaluation_ground_truth.recognizer_eval import evaluate
from evaluation_ground_truth.report import write_report


def get_existing_file(prompt: str) -> Path:
    """
    Prompt until a valid file path is entered.
    """
    while True:
        path = Path(input(prompt).strip().strip('"'))

        if path.exists() and path.is_file():
            return path

        print("\n❌ File not found.")
        print("Please enter a valid file path.\n")


def get_output_directory(prompt: str) -> Path:
    """
    Prompt for an output directory.
    Creates it if it does not exist.
    """
    path = Path(input(prompt).strip().strip('"'))

    path.mkdir(parents=True, exist_ok=True)

    return path


def main():

    print("=" * 70)
    print("      DECIMER Ground Truth Evaluation")
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

    print("\nLoading files...")
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
Recognition Rate     : {summary['recognition_rate']} %
Canonical Accuracy   : {summary['overall_accuracy']} %
Exact Accuracy       : {summary['exact_accuracy']} %
Missing Predictions  : {summary['missing']}
Invalid SMILES       : {summary['invalid_smiles']}
""")

    print("Reports saved to:")
    print(output_dir.resolve())

    print("\nGenerated Files:")
    print("  • evaluation_summary.json")
    print("  • evaluation_details.csv")
    print("  • evaluation_report.html")


if __name__ == "__main__":
    main()