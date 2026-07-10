"""
config.py

Global configuration for the DECIMER document processing pipeline.
"""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

# Project root (one level above core/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_ROOT = PROJECT_ROOT / "outputs"
TEMP_ROOT = PROJECT_ROOT / "temp"
LOG_ROOT = PROJECT_ROOT / "logs"

# Create required folders automatically
for directory in [OUTPUT_ROOT, TEMP_ROOT, LOG_ROOT]:
    directory.mkdir(parents=True, exist_ok=True)

# =============================================================================
# INPUT SETTINGS
# =============================================================================

SUPPORTED_INPUT_TYPES = [
    "path",
    "blob",
]

SUPPORTED_FILE_EXTENSIONS = [
    ".pdf",
]

# =============================================================================
# DOCUMENT SETTINGS
# =============================================================================

DOCUMENT_ID_METHOD = "sha256"

SKIP_EXISTING_DOCUMENTS = True

# =============================================================================
# OUTPUT FOLDER NAMES
# =============================================================================

PAGE_FOLDER_PREFIX = "page_"

RAW_IMAGE_FOLDER = "raw"
CROP_FOLDER = "crops"
CLEAN_FOLDER = "cleaned"

REDRAW_PNG_FOLDER = "redraw_png"
REDRAW_SVG_FOLDER = "redraw_svg"

CSV_FILENAME = "metadata.csv"
LOG_FILENAME = "process.log"

# =============================================================================
# PDF RENDER SETTINGS
# =============================================================================

RENDER_DPI = 300

IMAGE_FORMAT = "png"

PAGE_NAME_TEMPLATE = "page_{:03d}"

IMAGE_NAME_TEMPLATE = "image_{:03d}.png"

# =============================================================================
# DECIMER SEGMENTATION
# =============================================================================

SEGMENT_EXPAND = True

# =============================================================================
# IMAGE CLEANING
# =============================================================================

REMOVE_NOISE = True
DESKEW_IMAGES = True
BINARIZE_IMAGES = False

# =============================================================================
# DECIMER RECOGNITION
# =============================================================================

RUN_DECIMER = True

SAVE_SMILES = True

# =============================================================================
# METADATA COLUMNS
# =============================================================================

METADATA_COLUMNS = [

    "document_id",

    "pdf_name",

    "page_number",

    "image_id",

    "image_path",

    "clean_image_path",

    "image_type",

    "is_formula",

    "smiles",

    "processing_status",

    "error_message",

]

# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = "INFO"

ENABLE_FILE_LOGGING = True

ENABLE_CONSOLE_LOGGING = True

# =============================================================================
# TEMP FILES
# =============================================================================

DELETE_TEMP_FILES = False

# =============================================================================
# CONTAINER
# =============================================================================

CONTAINER_NAME = "decimer_pipeline"

PIPELINE_VERSION = "2.0.0"