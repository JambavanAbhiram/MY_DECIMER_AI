"""
cleaner.py

Image preprocessing module for DECIMER recognition.
"""

from pathlib import Path

import cv2
import numpy as np


class ImageCleaner:
    """
    Cleans segmented chemical structure images before
    DECIMER recognition.
    """

    def __init__(
        self,
        resize_width: int = 1024,
        padding: int = 20,
    ):
        self.resize_width = resize_width
        self.padding = padding

    # -------------------------------------------------------------

    def process(
        self,
        input_path,
        output_path,
    ):
        """
        Clean a cropped chemical structure image.

        Parameters
        ----------
        input_path : str | Path
            Cropped image.

        output_path : str | Path
            Destination for cleaned image.
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
                f"Failed to save cleaned image: {output_path}"
            )

        return output_path

    # -------------------------------------------------------------

    def _preprocess(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Basic preprocessing pipeline.
        """

        # Convert to grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        # Denoise
        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        # Otsu threshold
        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        # Ensure black structure on white background
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        # Crop surrounding whitespace
        coords = cv2.findNonZero(
            255 - binary
        )

        if coords is not None:

            x, y, w, h = cv2.boundingRect(coords)

            binary = binary[
                max(0, y - self.padding):
                min(binary.shape[0], y + h + self.padding),

                max(0, x - self.padding):
                min(binary.shape[1], x + w + self.padding),
            ]

        # Resize if needed
        h, w = binary.shape

        if w > self.resize_width:

            scale = self.resize_width / w

            binary = cv2.resize(
                binary,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA,
            )

        return binary