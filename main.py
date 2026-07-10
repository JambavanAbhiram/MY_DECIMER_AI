"""
main.py

Entry point for the DECIMER document processing pipeline.

Author: Abhiram
"""

from pathlib import Path

from pipeline import Pipeline


def main():

    print("=" * 60)
    print("DECIMER Document Processing Pipeline")
    print("=" * 60)

    pdf_path = input(
        "\nEnter PDF path (or drag & drop the PDF here):\n> "
    ).strip().strip('"')

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():

        print("\nERROR: PDF not found.")
        return

    if pdf_path.suffix.lower() != ".pdf":

        print("\nERROR: Input must be a PDF.")
        return

    pipeline = Pipeline()

    result = pipeline.run(pdf_path)

    print("\n" + "=" * 60)
    print("Pipeline Finished")
    print("=" * 60)

    print(f"Status        : {result['status']}")
    print(f"Document ID   : {result['document_id']}")

    if result["status"] == "SUCCESS":

        print(f"Output Folder : {result['output_directory']}")
        print(f"Metadata CSV  : {result['metadata_csv']}")

    else:

        print(f"Error         : {result['error']}")


if __name__ == "__main__":
    main()