"""
main.py

Entry point for the DECIMER Project.

Supports
--------
• Single PDF
• Single Image
• Folder of PDFs
• Folder of Images
• Mixed input

Author: DECIMER Project
"""

from pathlib import Path
import sys

from pipeline import Pipeline


# -------------------------------------------------------------

def print_banner():

    print("=" * 70)
    print("DECIMER Chemical Structure Recognition Pipeline")
    print("=" * 70)
    print()


# -------------------------------------------------------------

def get_inputs():
    """
    Ask the user for one or more input paths.

    Multiple paths can be separated by commas.

    Example
    -------
    D:/papers
    D:/paper.pdf
    D:/images,D:/paper.pdf
    """

    raw = input(
        "Enter a file or folder path\n"
        "(Multiple paths can be separated with commas)\n\n> "
    ).strip()

    if not raw:
        return []
    paths = []

    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        path = Path(item)
        if not path.exists():
            print(f"[WARNING] Path does not exist: {path}")
            continue
        paths.append(str(path))
    return paths


# -------------------------------------------------------------

def main():

    print_banner()
    inputs = get_inputs()

    if len(inputs) == 0:
        print("\nNo valid inputs were provided.")
        return

    print()
    pipeline = Pipeline()

    try:
        pipeline.run(inputs)

        print("\n")
        print("=" * 70)
        print("Pipeline completed successfully.")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        sys.exit(1)

    except Exception as exc:

        print("\nPipeline failed.")
        print(exc)

        raise


# -------------------------------------------------------------

if __name__ == "__main__":
    main()