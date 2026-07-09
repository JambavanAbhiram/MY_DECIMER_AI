"""
main.py

Entry point for the DECIMER pipeline.
"""

from pathlib import Path
import sys

from pipeline import Pipeline


def main():
    print("=" * 60)
    print("DECIMER Chemical Structure Recognition Pipeline")
    print("=" * 60)

    pdf_folder = input("Enter the path to the PDF folder: ").strip()

    if not pdf_folder:
        print("ERROR: No folder path provided.")
        sys.exit(1)

    pdf_folder = Path(pdf_folder)

    if not pdf_folder.exists():
        print(f"ERROR: Folder not found: {pdf_folder}")
        sys.exit(1)

    pipeline = Pipeline()

    try:
        pipeline.run(pdf_folder)
        print("\nPipeline completed successfully.")
    except Exception as e:
        print(f"\nERROR\n{'-' * 32}\n{e}")
        raise


if __name__ == "__main__":
    main()