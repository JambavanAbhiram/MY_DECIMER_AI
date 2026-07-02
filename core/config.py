"""
config.py

Global configuration for the DECIMER document processing pipeline.
"""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

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
    "blob"
]

SUPPORTED_FILE_EXTENSIONS = [
    ".pdf"
]


# =============================================================================
# DOCUMENT SETTINGS
# =============================================================================

# SHA256 is recommended for deterministic document IDs
DOCUMENT_ID_METHOD = "sha256"

# If False, existing outputs may be overwritten
SKIP_EXISTING_DOCUMENTS = True


# =============================================================================
# OUTPUT FOLDER NAMES
# =============================================================================

PAGE_FOLDER_PREFIX = "page_"

RAW_IMAGE_FOLDER = "raw"
CROP_FOLDER = "crops"
CLEAN_FOLDER = "cleaned"

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
# YOLO SETTINGS
# =============================================================================

YOLO_CONFIDENCE_THRESHOLD = 0.25

SAVE_DETECTION_VISUALIZATION = False


# =============================================================================
# IMAGE CLEANING
# =============================================================================

REMOVE_NOISE = True

DESKEW_IMAGES = True

BINARIZE_IMAGES = False


# =============================================================================
# DECIMER SETTINGS
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

    "error_message"

]


# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = "INFO"

ENABLE_FILE_LOGGING = True

ENABLE_CONSOLE_LOGGING = True


# =============================================================================
# TEMP FILE SETTINGS
# =============================================================================

DELETE_TEMP_FILES = False


# =============================================================================
# CONTAINER SETTINGS
# =============================================================================

CONTAINER_NAME = "decimer_pipeline"

PIPELINE_VERSION = "1.0.0"