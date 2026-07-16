"""
metrics.py

Summary metric computation for DECIMER Ground Truth Evaluation.
"""


def summarize(df):
    """
    Compute evaluation summary statistics.
    """

    total = len(df)

    recognized = (
        df["evaluation_status"].isin(
            ["Correct", "Incorrect", "Invalid SMILES"]
        )
    ).sum()

    missing = (
        df["evaluation_status"] == "Missing Prediction"
    ).sum()

    recognition_failed = (
        df["evaluation_status"] == "Recognition Failed"
    ).sum()

    invalid = (
        df["evaluation_status"] == "Invalid SMILES"
    ).sum()

    exact = (
        df["exact_match"] == True
    ).sum()

    canonical = (
        df["canonical_match"] == True
    ).sum()

    return {

        # ---------------------------------------------------------
        # Counts
        # ---------------------------------------------------------

        "total_formula_images": int(total),

        "recognized": int(recognized),

        "missing": int(missing),

        "recognition_failed": int(recognition_failed),

        "invalid_smiles": int(invalid),

        "exact_matches": int(exact),

        "canonical_matches": int(canonical),

        # ---------------------------------------------------------
        # Percentages
        # ---------------------------------------------------------

        # Percentage of images that produced a prediction
        "recognition_rate": round(
            (recognized / total) * 100, 2
        ) if total else 0,

        # Exact match accuracy among recognized structures
        "exact_accuracy": round(
            (exact / recognized) * 100, 2
        ) if recognized else 0,

        # Canonical accuracy among all formula images
        "overall_accuracy": round(
            (canonical / total) * 100, 2
        ) if total else 0,
    }