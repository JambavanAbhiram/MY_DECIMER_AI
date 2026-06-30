from pathlib import Path
from typing import Union

import cv2
import numpy as np


class ImageCleaner:
    """
    Performs preprocessing on chemical structure images before
    recognition.
    """

    def __init__(
        self,
        target_size: int = 512,
        padding: int = 20,
    ):
        self.target_size = target_size
        self.padding = padding

    # ---------------------------------------------------------

    def load(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Load an image from disk.
        """

        image = cv2.imread(str(image_path))

        if image is None:
            raise FileNotFoundError(image_path)

        return image

    # ---------------------------------------------------------

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:

        if len(image.shape) == 2:
            return image

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------------------------------

    def remove_border(self, image: np.ndarray) -> np.ndarray:
        """
        Removes excessive white border around the molecule.
        """

        coords = cv2.findNonZero(255 - image)

        if coords is None:
            return image

        x, y, w, h = cv2.boundingRect(coords)

        return image[y:y + h, x:x + w]

    # ---------------------------------------------------------

    def denoise(self, image: np.ndarray) -> np.ndarray:

        return cv2.fastNlMeansDenoising(
            image,
            None,
            15,
            7,
            21
        )

    # ---------------------------------------------------------

    def threshold(self, image: np.ndarray) -> np.ndarray:

        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10,
        )

    # ---------------------------------------------------------

    def resize(self, image: np.ndarray) -> np.ndarray:
        """
        Resize while maintaining aspect ratio.
        """

        h, w = image.shape[:2]

        scale = (
            self.target_size - 2 * self.padding
        ) / max(h, w)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA
        )

        canvas = np.full(
            (
                self.target_size,
                self.target_size
            ),
            255,
            dtype=np.uint8
        )

        x = (self.target_size - new_w) // 2
        y = (self.target_size - new_h) // 2

        canvas[
            y:y + new_h,
            x:x + new_w
        ] = resized

        return canvas

    # ---------------------------------------------------------

    def invert_if_needed(self, image: np.ndarray) -> np.ndarray:
        """
        Ensures black structure on white background.
        """

        black_pixels = np.sum(image < 128)
        white_pixels = np.sum(image >= 128)

        if black_pixels > white_pixels:
            image = cv2.bitwise_not(image)

        return image

    # ---------------------------------------------------------

    def clean(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Complete preprocessing pipeline.
        """

        image = self.load(image_path)

        image = self.to_grayscale(image)

        image = self.remove_border(image)

        image = self.denoise(image)

        image = self.threshold(image)

        image = self.invert_if_needed(image)

        image = self.resize(image)

        return image

    # ---------------------------------------------------------

    def save(
        self,
        image: np.ndarray,
        output_path: Union[str, Path],
    ):
        """
        Save processed image.
        """

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cv2.imwrite(
            str(output_path),
            image,
        )

    # ---------------------------------------------------------

    def process(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
    ) -> Path:
        """
        Clean and save image.

        Returns
        -------
        Path
            Path to cleaned image.
        """

        cleaned = self.clean(image_path)

        self.save(
            cleaned,
            output_path,
        )

        return Path(output_path)