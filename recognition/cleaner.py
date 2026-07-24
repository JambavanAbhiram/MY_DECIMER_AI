"""
cleaner.py

Advanced image preprocessing module for DECIMER recognition.
Improved for chemical structure OCR.
"""

from pathlib import Path

import cv2
import numpy as np


class ImageCleaner:
    """
    Advanced preprocessing pipeline for segmented
    chemical structure images.
    """

    def __init__(
        self,
        resize_width: int = 1024,
        padding: int = 20,
        clahe_clip: float = 2.5,
        clahe_grid=(8, 8),
    ):
        self.resize_width = resize_width
        self.padding = padding
        self.clahe_clip = clahe_clip
        self.clahe_grid = clahe_grid

    # ---------------------------------------------------------

    def process(
        self,
        input_path,
        output_path,
    ):
        """
        Clean a cropped chemical structure image.
        """

        input_path = Path(input_path)
        output_path = Path(output_path)

        image = cv2.imread(str(input_path))

        if image is None:
            raise FileNotFoundError(
                f"Unable to load image: {input_path}"
            )

        cleaned = self._preprocess(image)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        success = cv2.imwrite(
            str(output_path),
            cleaned,
        )

        if not success:
            raise RuntimeError(
                f"Failed to save image: {output_path}"
            )

        return output_path

    # ---------------------------------------------------------

    def _preprocess(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        #
        # STEP 1
        # Convert to grayscale
        #

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        #
        # STEP 2
        # CLAHE Contrast Enhancement
        #

        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip,
            tileGridSize=self.clahe_grid,
        )

        gray = clahe.apply(gray)

        #
        # STEP 3
        # Edge-preserving denoising
        #

        gray = cv2.bilateralFilter(
            gray,
            d=5,
            sigmaColor=50,
            sigmaSpace=50,
        )

        #
        # STEP 4
        # Adaptive Threshold
        #

        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            7,
        )

        #
        # STEP 5
        # Ensure black structure on white background
        #

        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        #
        # STEP 6
        # Morphological Closing
        # Connect broken bonds
        #

        kernel = np.ones((2, 2), np.uint8)

        binary = cv2.morphologyEx(
            binary,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1,
        )

        #
        # STEP 7
        # Morphological Opening
        # Remove isolated noise
        #

        binary = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1,
        )

        #
        # STEP 8
        # Crop surrounding whitespace
        #

        coords = cv2.findNonZero(
            255 - binary
        )

        if coords is not None:

            x, y, w, h = cv2.boundingRect(coords)

            x1 = max(0, x - self.padding)
            y1 = max(0, y - self.padding)

            x2 = min(
                binary.shape[1],
                x + w + self.padding,
            )

            y2 = min(
                binary.shape[0],
                y + h + self.padding,
            )

            binary = binary[
                y1:y2,
                x1:x2,
            ]

        #
        # STEP 9
        # Add white border
        #

        binary = cv2.copyMakeBorder(
            binary,
            15,
            15,
            15,
            15,
            cv2.BORDER_CONSTANT,
            value=255,
        )

        #
        # STEP 10
        # Resize while preserving aspect ratio
        #

        h, w = binary.shape

        max_dim = max(h, w)

        if max_dim > self.resize_width:

            scale = self.resize_width / max_dim

            binary = cv2.resize(
                binary,
                (
                    int(w * scale),
                    int(h * scale),
                ),
                interpolation=cv2.INTER_AREA,
            )

        return binary

