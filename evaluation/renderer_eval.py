"""
evaluation/renderer_eval.py

Evaluation utilities for validating rendered PDF pages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import cv2
import numpy as np
import pandas as pd


class RendererEvaluator:
    """
    Evaluates rendered PDF page images.
    """

    REQUIRED_COLUMNS = [
        "page_number",
        "image_path",
    ]

    def __init__(self, metadata_csv: str | Path):

        self.metadata_csv = Path(metadata_csv)

        if not self.metadata_csv.exists():
            raise FileNotFoundError(
                f"{self.metadata_csv} does not exist."
            )

        self.df = pd.read_csv(self.metadata_csv)

        self.results: Dict[str, object] = {}

    # ---------------------------------------------------------
    # Column Validation
    # ---------------------------------------------------------

    def validate_columns(self):

        missing = [
            c
            for c in self.REQUIRED_COLUMNS
            if c not in self.df.columns
        ]

        self.results["missing_columns"] = missing

        return len(missing) == 0

    # ---------------------------------------------------------
    # File Validation
    # ---------------------------------------------------------

    def validate_image_paths(self):

        missing = 0

        for path in self.df["image_path"]:

            if not Path(path).exists():
                missing += 1

        self.results["missing_images"] = missing

    # ---------------------------------------------------------
    # Image Readability
    # ---------------------------------------------------------

    def validate_readable_images(self):

        unreadable = 0

        for path in self.df["image_path"]:

            image = cv2.imread(str(path))

            if image is None:
                unreadable += 1

        self.results["unreadable_images"] = unreadable

    # ---------------------------------------------------------
    # Blank Images
    # ---------------------------------------------------------

    def validate_blank_images(self):

        blank = 0

        for path in self.df["image_path"]:

            image = cv2.imread(str(path))

            if image is None:
                continue

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )

            if np.std(gray) < 2:
                blank += 1

        self.results["blank_images"] = blank

    # ---------------------------------------------------------
    # Image Dimensions
    # ---------------------------------------------------------

    def validate_dimensions(self):

        invalid = 0

        widths = []
        heights = []

        for path in self.df["image_path"]:

            image = cv2.imread(str(path))

            if image is None:
                continue

            h, w = image.shape[:2]

            widths.append(w)
            heights.append(h)

            if w <= 0 or h <= 0:
                invalid += 1

        self.results["invalid_dimensions"] = invalid

        if widths:

            self.results["average_width"] = round(
                float(np.mean(widths)),
                2,
            )

            self.results["average_height"] = round(
                float(np.mean(heights)),
                2,
            )

    # ---------------------------------------------------------
    # Image Format
    # ---------------------------------------------------------

    def validate_format(self):

        invalid = 0

        for path in self.df["image_path"]:

            suffix = Path(path).suffix.lower()

            if suffix not in [".png", ".jpg", ".jpeg"]:

                invalid += 1

        self.results["invalid_format"] = invalid

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summarize(self):

        self.results["rendered_pages"] = len(self.df)

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------

    def evaluate(self):

        if not self.validate_columns():
            return self.results

        self.validate_image_paths()

        self.validate_readable_images()

        self.validate_blank_images()

        self.validate_dimensions()

        self.validate_format()

        self.summarize()

        return self.results

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_dataframe(self):

        return pd.DataFrame(
            [
                {
                    "metric": k,
                    "value": v,
                }
                for k, v in self.results.items()
            ]
        )

    def save(self, output_path):

        self.to_dataframe().to_csv(
            output_path,
            index=False,
        )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def print_summary(self):

        print("\nRenderer Evaluation")
        print("-" * 40)

        for k, v in self.results.items():
            print(f"{k:<30}{v}")