from pathlib import Path

import cv2
import numpy as np


class ImageCleaner:
    """
    Cleans segmented chemical structure images before DECIMER recognition.
    """

    def __init__(
        self,
        output_dir: str | Path,
        resize_width: int = 1024,
        padding: int = 20,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.resize_width = resize_width
        self.padding = padding

    def clean_image(self, image_path: str | Path) -> Path:
        """
        Clean a single cropped chemical structure image.

        Parameters
        ----------
        image_path : str | Path

        Returns
        -------
        Path
            Path to cleaned image.
        """

        image_path = Path(image_path)

        image = cv2.imread(str(image_path))

        if image is None:
            raise FileNotFoundError(f"Cannot load image: {image_path}")

        cleaned = self._preprocess(image)

        output_path = self.output_dir / image_path.name

        cv2.imwrite(str(output_path), cleaned)

        return output_path

    def _preprocess(self, image: np.ndarray) -> np.ndarray:

        # grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # denoise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # threshold
        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        # invert if necessary
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        # crop white border
        coords = cv2.findNonZero(255 - binary)

        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)

            binary = binary[
                max(0, y - self.padding): y + h + self.padding,
                max(0, x - self.padding): x + w + self.padding,
            ]

        # resize
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