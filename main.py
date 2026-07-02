"""
main.py

Entry point for the DECIMER document processing pipeline.

Supports:
    1. PDF file path
    2. PDF blob (bytes)

Author: Abhiram
"""

from pathlib import Path

from pipeline import Pipeline


def get_user_input():
    """
    Ask the user for the PDF path.
    """

    print("\n===============================")
    print(" DECIMER Document Pipeline")
    print("===============================\n")

    pdf_path = input("Enter the full path to the PDF file:\n> ").strip()

    if not pdf_path:
        raise ValueError("No PDF path was provided.")

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"\nFile not found:\n{pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    return pdf_path


def process_pdf_path():
    """
    Process a PDF from its file path.
    """

    pdf_path = get_user_input()

    pipeline = Pipeline()

    result = pipeline.run(pdf_path)

    print("\n================================")
    print(" Processing Complete")
    print("================================")

    print(f"Document ID : {result['document_id']}")
    print(f"Output Path : {result['output_directory']}")
    print(f"CSV File    : {result['metadata_csv']}")


def process_pdf_blob(pdf_blob: bytes):
    """
    Process a PDF already loaded into memory.
    This method will be used later by APIs,
    Docker containers, Workato, etc.
    """

    pipeline = Pipeline()

    return pipeline.run(pdf_blob)


def main():
    """
    Local execution entry point.
    """

    try:
        process_pdf_path()

    except Exception as e:
        print("\nERROR")
        print("--------------------------------")
        print(e)


if __name__ == "__main__":
    main()