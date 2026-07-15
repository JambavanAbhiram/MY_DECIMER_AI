"""
report.py

Generates evaluation reports for the DECIMER Ground Truth Evaluation.
"""

import json
from pathlib import Path

from evaluation_ground_truth.config import (
    SUMMARY_JSON,
    DETAILS_CSV,
    REPORT_HTML,
    REPORT_TITLE,
)


def write_report(summary, details, output_dir):
    """
    Generate all evaluation reports.

    Parameters
    ----------
    summary : dict
        Summary statistics.
    details : pandas.DataFrame
        Row-wise evaluation results.
    output_dir : Path
        Output directory.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------
    # Save Detailed CSV
    # ----------------------------------------------------------

    details_path = output_dir / DETAILS_CSV
    details.to_csv(details_path, index=False)

    # ----------------------------------------------------------
    # Save Summary JSON
    # ----------------------------------------------------------

    summary_path = output_dir / SUMMARY_JSON

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    # ----------------------------------------------------------
    # Prepare Failure Table
    # ----------------------------------------------------------

    failures = details[
        details["evaluation_status"] != "Correct"
    ]

    if failures.empty:
        failure_table = "<p>No failed predictions 🎉</p>"
    else:
        failure_table = failures.to_html(
            index=False,
            escape=False
        )

    # ----------------------------------------------------------
    # HTML Report
    # ----------------------------------------------------------

    html = f"""
<!DOCTYPE html>
<html>

<head>

<title>{REPORT_TITLE}</title>

<style>

body {{
    font-family: Arial, Helvetica, sans-serif;
    margin: 40px;
    background-color: #fafafa;
}}

h1 {{
    color: #1f4e79;
}}

h2 {{
    margin-top: 40px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
}}

th {{
    background: #1f4e79;
    color: white;
    padding: 10px;
}}

td {{
    border: 1px solid #cccccc;
    padding: 8px;
}}

tr:nth-child(even) {{
    background: #f2f2f2;
}}

.summary {{
    width: 45%;
}}

</style>

</head>

<body>

<h1>{REPORT_TITLE}</h1>

<h2>Summary</h2>

<table class="summary">

<tr><th>Metric</th><th>Value</th></tr>

<tr><td>Total Formula Images</td><td>{summary["total_formula_images"]}</td></tr>

<tr><td>Recognized</td><td>{summary["recognized"]}</td></tr>

<tr><td>Missing</td><td>{summary["missing"]}</td></tr>

<tr><td>Invalid SMILES</td><td>{summary["invalid_smiles"]}</td></tr>

<tr><td>Exact Matches</td><td>{summary["exact_matches"]}</td></tr>

<tr><td>Canonical Matches</td><td>{summary["canonical_matches"]}</td></tr>

<tr><td>Recognition Rate (%)</td><td>{summary["recognition_rate"]}</td></tr>

<tr><td>Exact Accuracy (%)</td><td>{summary["exact_accuracy"]}</td></tr>

<tr><td>Overall Accuracy (%)</td><td>{summary["overall_accuracy"]}</td></tr>

</table>

<h2>Failed Predictions</h2>

{failure_table}

</body>

</html>
"""

    report_path = output_dir / REPORT_HTML

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("\nSaved Files")
    print("-" * 40)
    print(details_path)
    print(summary_path)
    print(report_path)