from typing import Dict
from pathlib import Path
from unittest import result

import cv2
import numpy as np


class VariantGenerator:
    """
    Generates multiple image variants for
    ensemble recognition.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------

    @staticmethod
    def original(image: np.ndarray) -> np.ndarray:
        return image.copy()

    # ---------------------------------------------------------

    @staticmethod
    @staticmethod
    def adaptive(image):

        if len(image.shape) == 3:
            image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        image = image.astype(np.uint8)

        return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)

    # ---------------------------------------------------------

    @staticmethod
    def otsu(image):

        # Convert BGR → Grayscale if needed
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Ensure uint8
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

        _, result = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,)

        return result

    # ---------------------------------------------------------

    @staticmethod
    def inverted(image: np.ndarray) -> np.ndarray:

        return cv2.bitwise_not(image)

    # ---------------------------------------------------------

    @staticmethod
    def sharpen(image: np.ndarray) -> np.ndarray:

        kernel = np.array(
            [
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0],
            ],
            dtype=np.float32,
        )

        return cv2.filter2D(
            image,
            -1,
            kernel,
        )

    # ---------------------------------------------------------

    @staticmethod
    def median(image: np.ndarray) -> np.ndarray:

        return cv2.medianBlur(
            image,
            3,
        )

    # ---------------------------------------------------------

    @staticmethod
    def gaussian(image: np.ndarray) -> np.ndarray:

        return cv2.GaussianBlur(
            image,
            (3, 3),
            0,
        )

    # ---------------------------------------------------------

    @staticmethod
    def morphology_open(image: np.ndarray) -> np.ndarray:

        kernel = np.ones(
            (2, 2),
            np.uint8,
        )

        return cv2.morphologyEx(
            image,
            cv2.MORPH_OPEN,
            kernel,
        )

    # ---------------------------------------------------------

    @staticmethod
    def morphology_close(image: np.ndarray) -> np.ndarray:

        kernel = np.ones(
            (2, 2),
            np.uint8,
        )

        return cv2.morphologyEx(
            image,
            cv2.MORPH_CLOSE,
            kernel,
        )

    # ---------------------------------------------------------

    @staticmethod
    def dilated(image: np.ndarray) -> np.ndarray:

        kernel = np.ones(
            (2, 2),
            np.uint8,
        )

        return cv2.dilate(
            image,
            kernel,
            iterations=1,
        )

    # ---------------------------------------------------------

    @staticmethod
    def eroded(image: np.ndarray) -> np.ndarray:

        kernel = np.ones(
            (2, 2),
            np.uint8,
        )

        return cv2.erode(
            image,
            kernel,
            iterations=1,
        )

    # ---------------------------------------------------------

    def generate(self, image):
        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image), cv2.IMREAD_GRAYSCALE)

        # If it's a color image, convert to grayscale
        elif len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ensure uint8
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

    # ---------------------------------------------------------

    def __call__(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Allows direct calling:

        variants = VariantGenerator()(image)
        """
        return self.generate(image)