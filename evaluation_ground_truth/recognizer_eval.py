"""
recognizer_eval.py

Core evaluation module for DECIMER Ground Truth Evaluation.

Compares pipeline predictions stored in metadata.csv against
ground truth annotations provided in Excel.
"""

import pandas as pd

from evaluation_ground_truth.utils import canonicalize
from evaluation_ground_truth.metrics import summarize

from evaluation_ground_truth.config import (
    REQUIRED_GT_COLUMNS,
    REQUIRED_METADATA_COLUMNS,
    GT_IMAGE_ID,
    GT_SMILES,
    GT_USE_FOR_EVAL,
    META_IMAGE_ID,
    META_SMILES,
    META_STATUS,
    META_ERROR,
    STATUS_SUCCESS,
)


# -------------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------------

def validate_columns(df, required_columns, dataframe_name):
    """
    Ensure all required columns exist.
    """

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"\n{dataframe_name} is missing required columns:\n"
            + "\n".join(missing)
        )


# -------------------------------------------------------------------------
# Loaders
# -------------------------------------------------------------------------

def load_ground_truth(gt_path):
    """
    Load and filter ground truth.
    """

    gt = pd.read_excel(gt_path)

    validate_columns(
        gt,
        REQUIRED_GT_COLUMNS,
        "Ground Truth"
    )

    gt = gt[gt[GT_USE_FOR_EVAL] == True].copy()

    gt[GT_IMAGE_ID] = gt[GT_IMAGE_ID].astype(str).str.strip()

    return gt


def load_metadata(metadata_path):
    """
    Load pipeline metadata.
    """

    meta = pd.read_csv(metadata_path)

    validate_columns(
        meta,
        REQUIRED_METADATA_COLUMNS,
        "Metadata"
    )

    meta[META_IMAGE_ID] = meta[META_IMAGE_ID].astype(str).str.strip()

    return meta


# -------------------------------------------------------------------------
# Evaluation
# -------------------------------------------------------------------------

def evaluate(gt_path, metadata_path):

    print("Loading Ground Truth...")
    gt = load_ground_truth(gt_path)

    print("Loading Metadata...")
    meta = load_metadata(metadata_path)

    print("Matching image IDs...")

    df = gt.merge(
        meta,
        left_on=GT_IMAGE_ID,
        right_on=META_IMAGE_ID,
        how="left",
        suffixes=("_gt", "_pred")
    )

    print("Canonicalizing SMILES...")

    df["ground_truth_canonical"] = (
        df[GT_SMILES]
        .fillna("")
        .apply(canonicalize)
    )

    df["predicted_canonical"] = (
        df[META_SMILES]
        .fillna("")
        .apply(canonicalize)
    )

    print("Computing matches...")

    df["exact_match"] = (
        df[GT_SMILES]
        .fillna("")
        .astype(str)
        .str.strip()
        ==
        df[META_SMILES]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["canonical_match"] = (
        df["ground_truth_canonical"]
        ==
        df["predicted_canonical"]
    )

    # ---------------------------------------------------------------
    # Status Classification
    # ---------------------------------------------------------------

    def classify(row):

        status = str(row.get(META_STATUS, "")).upper()

        predicted = str(row.get(META_SMILES, "")).strip()

        canonical = row.get("predicted_canonical")

        if status != STATUS_SUCCESS:
            return "Recognition Failed"

        if predicted == "":
            return "Missing Prediction"

        if pd.isna(canonical):
            return "Invalid SMILES"

        if row["canonical_match"]:
            return "Correct"

        return "Incorrect"

    df["evaluation_status"] = df.apply(
        classify,
        axis=1
    )

    print("Generating summary metrics...")

    summary = summarize(df)

    return df, summary