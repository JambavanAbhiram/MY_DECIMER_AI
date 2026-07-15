"""
config.py

Configuration constants for the DECIMER Ground Truth Evaluation package.

All file and folder paths are collected interactively in benchmark.py.
This file only contains reusable constants and expected column names.
"""

from pathlib import Path

# =============================================================================
# Output Files
# =============================================================================

SUMMARY_JSON = "evaluation_summary.json"
DETAILS_CSV = "evaluation_details.csv"
REPORT_HTML = "evaluation_report.html"

# =============================================================================
# Ground Truth Columns
# =============================================================================

GT_IMAGE_ID = "image_id"
GT_SMILES = "ground_truth_smiles"
GT_USE_FOR_EVAL = "use_for_smiles_accuracy"

# =============================================================================
# Metadata Columns
# =============================================================================

META_IMAGE_ID = "image_id"
META_SMILES = "smiles"
META_STATUS = "processing_status"
META_ERROR = "error_message"
META_CONFIDENCE = "confidence"

# =============================================================================
# Processing Status Values
# =============================================================================

STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"

# =============================================================================
# Required Columns Validation
# =============================================================================

REQUIRED_GT_COLUMNS = [
    GT_IMAGE_ID,
    GT_SMILES,
    GT_USE_FOR_EVAL,
]

REQUIRED_METADATA_COLUMNS = [
    META_IMAGE_ID,
    META_SMILES,
    META_STATUS,
]

# =============================================================================
# RDKit Canonicalization
# =============================================================================

CANONICALIZE_SMILES = True

# =============================================================================
# Report Title
# =============================================================================

REPORT_TITLE = "DECIMER Ground Truth Evaluation Report"