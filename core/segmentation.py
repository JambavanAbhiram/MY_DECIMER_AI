"""
segmentation.py

Chemical Structure Detection & Segmentation

Responsibilities
----------------
1. Detect chemical structures using YOLO.
2. Crop each detected structure.
3. Save cropped images.
4. Return crop information.

Author: Abhiram
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
from ultralytics import YOLO

from core.config import (
    CROP_FOLDER,
    IMAGE_NAME_TEMPLATE,
    YOLO_CONFIDENCE_THRESHOLD,
)


@dataclass
class Detection:
    image_id: int
    image_path: Path
    image_type: str
    is_formula: bool
    confidence: float
    bbox: tuple


class StructureSegmenter:

    def __init__(self, model_path=None):
        """
        Load the trained YOLO model.
        """

        if model_path is None:
            project_root = Path(__file__).resolve().parent.parent
            model_path = project_root / "models" / "yolo" / "best.pt"

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                "\n"
                "YOLO model not found!\n\n"
                f"Expected:\n{self.model_path}\n\n"
                "Please place your trained 'best.pt' inside:\n"
                "models/yolo/"
            )

        self.model = YOLO(str(self.model_path))

    def segment(
        self,
        page_image: Path,
        output_directory: Path
    ):
        """
        Detect and crop chemical structures.
        """

        page_image = Path(page_image)

        image = cv2.imread(str(page_image))

        if image is None:
            raise FileNotFoundError(
                f"Unable to read image:\n{page_image}"
            )

        crop_folder = output_directory / CROP_FOLDER
        crop_folder.mkdir(parents=True, exist_ok=True)

        detections = []

        results = self.model.predict(
            source=image,
            conf=YOLO_CONFIDENCE_THRESHOLD,
            verbose=False
        )

        image_counter = 1

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                confidence = float(box.conf[0])

                crop = image[y1:y2, x1:x2]

                filename = IMAGE_NAME_TEMPLATE.format(
                    image_counter
                )

                crop_path = crop_folder / filename

                cv2.imwrite(
                    str(crop_path),
                    crop
                )

                detections.append(
                    Detection(
                        image_id=image_counter,
                        image_path=crop_path,
                        image_type="chemical_structure",
                        is_formula=True,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2)
                    )
                )

                image_counter += 1

        return detections