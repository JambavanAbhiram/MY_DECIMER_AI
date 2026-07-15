"""
metrics.py

Summary metric computation for DECIMER Ground Truth Evaluation.
"""

def summarize(df):

    total = len(df)

    recognized = (df["evaluation_status"] != "Recognition Failed").sum()

    missing = (df["evaluation_status"] == "Missing Prediction").sum()

    invalid = (df["evaluation_status"] == "Invalid SMILES").sum()

    exact = df["exact_match"].sum()

    canonical = df["canonical_match"].sum()

    return {

        "total_formula_images": int(total),

        "recognized": int(recognized),

        "missing": int(missing),

        "invalid_smiles": int(invalid),

        "exact_matches": int(exact),

        "canonical_matches": int(canonical),

        "recognition_rate": round(
            recognized / total * 100, 2
        ) if total else 0,

        "exact_accuracy": round(
            exact / recognized * 100, 2
        ) if recognized else 0,

        "overall_accuracy": round(
            canonical / total * 100, 2
        ) if total else 0
    }