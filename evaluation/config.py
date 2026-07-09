"""
evaluation/config.py

Configuration for the pipeline evaluation framework.

This module contains settings used exclusively by the evaluation
package and should not modify the behavior of the processing pipeline.
"""

from pathlib import Path

# ---------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------

# Root directory where evaluation outputs are stored
EVALUATION_DIR = Path("evaluation_results")

# Reports
REPORTS_DIR = EVALUATION_DIR / "reports"

# Generated plots
PLOTS_DIR = EVALUATION_DIR / "plots"

# Log files
LOGS_DIR = EVALUATION_DIR / "logs"

# Failed images
FAILED_DIR = EVALUATION_DIR / "failed_images"

# ---------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------

SAVE_RUNTIME_LOG = True

# ---------------------------------------------------------------------
# Resource Monitoring
# ---------------------------------------------------------------------

MONITOR_CPU = True
MONITOR_RAM = True
MONITOR_GPU = True

# ---------------------------------------------------------------------
# Detection Evaluation
# ---------------------------------------------------------------------

IOU_THRESHOLD = 0.50

# ---------------------------------------------------------------------
# Recognition Evaluation
# ---------------------------------------------------------------------

SMILES_MATCH_MODE = "canonical"

# ---------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------

SAVE_CSV = True
SAVE_JSON = True
GENERATE_PLOTS = True
GENERATE_SUMMARY = True

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

VERBOSE = True

# ---------------------------------------------------------------------
# Create directories automatically
# ---------------------------------------------------------------------

for directory in (
    EVALUATION_DIR,
    REPORTS_DIR,
    PLOTS_DIR,
    LOGS_DIR,
    FAILED_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)