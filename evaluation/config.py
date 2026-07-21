"""
config.py

Configuration for the DECIMER Evaluation Framework.
"""

from pathlib import Path

# =========================================================
# Output Configuration
# =========================================================

DEFAULT_OUTPUT_DIR = Path("evaluation_results")

SUMMARY_CSV = "evaluation_summary.csv"

SUMMARY_JSON = "evaluation_summary.json"

DETAILS_CSV = "evaluation_details.csv"

FAILURES_CSV = "evaluation_failures.csv"

HTML_REPORT = "evaluation_report.html"

# =========================================================
# Image Validation
# =========================================================

VALID_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}

BLANK_IMAGE_THRESHOLD = 2.0

# =========================================================
# Ground Truth Evaluation
# =========================================================

GROUND_TRUTH_IMAGE_ID = "image_id"

GROUND_TRUTH_SMILES = "ground_truth_smiles"

# =========================================================
# Metadata Columns
# =========================================================

INVENTORY_REQUIRED_COLUMNS = [
    "document_id",
    "pdf_name",
    "pdf_path",
    "processed",
]

METADATA_REQUIRED_COLUMNS = [
    "document_id",
    "page_number",
    "image_id",
    "image_path",
]

RECOGNITION_REQUIRED_COLUMNS = [
    "image_id",
    "smiles",
]

# =========================================================
# Runtime
# =========================================================

DECIMAL_PRECISION = 2