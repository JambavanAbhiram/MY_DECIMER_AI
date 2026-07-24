"""
recognition/processor.py

Coordinates preprocessing, recognition, validation and selection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .cleaner import ImageCleaner
from .recognizer import Recognizer
from .validator import SmilesValidator
from .selector import RecognitionSelector
from .result import RecognitionResult


class RecognitionProcessor:
    def __init__(
        self,
        cleaner: ImageCleaner | None = None,
        recognizer: Recognizer | None = None,
        validator: SmilesValidator | None = None,
        selector: RecognitionSelector | None = None,
    ):
        self.cleaner = cleaner or ImageCleaner()
        self.recognizer = recognizer or Recognizer()
        self.validator = validator or SmilesValidator()
        self.selector = selector or RecognitionSelector()

    def process(self, image_path: str | Path) -> RecognitionResult:
        image_path = Path(image_path)

        cleaned_image = self.cleaner.process(image_path)

        results = self.recognizer.recognize(cleaned_image)

        best_result = self.selector.select(results)

        validation = self.validator(best_result.smiles)

        best_result.metadata.update({
            "validation": validation,
            "cleaned_image": str(cleaned_image),
            "source_image": str(image_path),
        })

        if validation["valid"]:
            best_result.smiles = validation["canonical_smiles"]

        return best_result

    def process_batch(
        self,
        images: Iterable[str | Path],
    ) -> list[RecognitionResult]:
        outputs = []

        for image in images:
            outputs.append(self.process(image))

        return outputs

    def __call__(self, image_path):
        return self.process(image_path)
