"""
core/config.py

Global configuration for the DECIMER Project.

Author: DECIMER Project
"""

from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ==========================================================
# INPUT
# ==========================================================

INPUT_FOLDER = PROJECT_ROOT / "input"

# ==========================================================
# OUTPUT
# ==========================================================

OUTPUT_FOLDER = PROJECT_ROOT / "output"

RENDERED_FOLDER = OUTPUT_FOLDER / "rendered_pages"

SEGMENTED_FOLDER = OUTPUT_FOLDER / "segmented_structures"

CLEANED_FOLDER = OUTPUT_FOLDER / "cleaned_structures"

REDRAW_FOLDER = OUTPUT_FOLDER / "redraw"

REDRAW_PNG_FOLDER = REDRAW_FOLDER / "png"

REDRAW_SVG_FOLDER = REDRAW_FOLDER / "svg"

LOG_FOLDER = OUTPUT_FOLDER / "logs"

METADATA_FOLDER = OUTPUT_FOLDER / "metadata"

TEMP_FOLDER = OUTPUT_FOLDER / "_tmp"

# ==========================================================
# DATABASES
# ==========================================================

MASTER_DATABASE = METADATA_FOLDER / "master_database.csv"

DOCUMENT_DATABASE = METADATA_FOLDER / "document_database.csv"

# ==========================================================
# MODELS
# ==========================================================

MODELS_FOLDER = PROJECT_ROOT / "models"

YOLO_MODEL = MODELS_FOLDER / "best.pt"

# ==========================================================
# RECOGNITION
# ==========================================================

ENABLE_DECIMER = True

ENABLE_MOLSCRIBE = True

TRY_HAND_DRAWN = True

USE_PUBCHEM = True

# ==========================================================
# IMAGE PROCESSING
# ==========================================================

DEFAULT_DPI = 300

TARGET_IMAGE_SIZE = 512

IMAGE_PADDING = 20

# ==========================================================
# FILE TYPES
# ==========================================================

SUPPORTED_PDFS = {
    ".pdf",
}

SUPPORTED_IMAGES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
}

# ==========================================================
# IMAGE TYPES
# ==========================================================

IMAGE_TYPE_FORMULA = "FORMULA"

IMAGE_TYPE_FIGURE = "FIGURE"

IMAGE_TYPE_UNKNOWN = "UNKNOWN"

# ==========================================================
# PIPELINE STATUS
# ==========================================================

STATUS_PENDING = "PENDING"

STATUS_RENDERED = "RENDERED"

STATUS_SEGMENTED = "SEGMENTED"

STATUS_CLEANED = "CLEANED"

STATUS_RECOGNIZED = "RECOGNIZED"

STATUS_FAILED = "FAILED"

STATUS_SKIPPED = "SKIPPED"

# ==========================================================
# MASTER DATABASE COLUMNS
# ==========================================================

MASTER_DATABASE_COLUMNS = [

    "doc_id",

    "pdf_name",

    "page_number",

    "image_id",

    "image_path",

    "clean_path",

    "redraw_png",

    "redraw_svg",

    "image_type",

    "is_formula",

    "smiles",

    "formula",

    "molecular_weight",

    "confidence",

    "agreement",

    "votes",

    "pubchem",

    "needs_review",

    "processed",

]

# ==========================================================
# DOCUMENT DATABASE COLUMNS
# ==========================================================

DOCUMENT_DATABASE_COLUMNS = [

    "doc_id",

    "pdf_name",

    "pdf_hash",

    "processed_on",

]

# ==========================================================
# CREATE DIRECTORIES
# ==========================================================

DIRECTORIES = [

    INPUT_FOLDER,

    OUTPUT_FOLDER,

    RENDERED_FOLDER,

    SEGMENTED_FOLDER,

    CLEANED_FOLDER,

    REDRAW_FOLDER,

    REDRAW_PNG_FOLDER,

    REDRAW_SVG_FOLDER,

    LOG_FOLDER,

    METADATA_FOLDER,

    TEMP_FOLDER,

    MODELS_FOLDER,

]

# ==========================================================
# CREATE ALL DIRECTORIES
# ==========================================================

for directory in DIRECTORIES:
    directory.mkdir(parents=True, exist_ok=True)