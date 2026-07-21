"""
recognition/recognizer.py

High-level recognition orchestrator.

Pipeline
--------
Image
   │
   ├── DECIMER Engine
   ├── MolScribe Engine
   │
Recognition Results
   │
Selector
   │
Validator
   │
RecognitionResult
"""

from __future__ import annotations

from pathlib import Path

from .decimer_engine import DecimerEngine
from .molscribe_engine import MolScribeEngine
from .selector import RecognitionSelector
from .validator import SmilesValidator


class ChemicalRecognizer:
    """
    Main recognition pipeline.

    Responsibilities
    ----------------
    1. Execute all recognition engines.
    2. Select the best prediction.
    3. Validate the selected SMILES.
    4. Return a standardized RecognitionResult.
    """

    def __init__(
        self,
        use_decimer: bool = True,
        use_molscribe: bool = True,
        hand_drawn: bool = False,
    ):

        self.engines = []

        if use_decimer:
            self.engines.append(
                DecimerEngine(
                    hand_drawn=hand_drawn
                )
            )

        if use_molscribe:
            self.engines.append(
                MolScribeEngine()
            )

        self.selector = RecognitionSelector()
        self.validator = SmilesValidator()

    # ---------------------------------------------------------

    def recognize(
        self,
        image_path: str | Path,
    ):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        engine_results = []

        # ---------------------------------------------
        # Run every recognition engine
        # ---------------------------------------------

        for engine in self.engines:

            result = engine.recognize(
                image_path
            )

            engine_results.append(result)

        # ---------------------------------------------
        # Select best prediction
        # ---------------------------------------------

        selected = self.selector.select(
            engine_results
        )

        if selected.smiles is None:

            selected.metadata["valid"] = False
            selected.metadata["engines"] = engine_results

            return selected

        # ---------------------------------------------
        # Validate selected SMILES
        # ---------------------------------------------

        validation = self.validator.validate(
            selected.smiles
        )

        selected.metadata.update(validation)

        selected.metadata["engines"] = engine_results

        if validation["valid"]:
            selected.smiles = validation[
                "canonical_smiles"
            ]

        return selected

    # ---------------------------------------------------------

    def recognize_folder(
        self,
        folder: str | Path,
    ):

        folder = Path(folder)

        extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tif",
            ".tiff",
        }

        results = []

        for image in sorted(folder.iterdir()):

            if (
                image.is_file()
                and image.suffix.lower() in extensions
            ):

                results.append(
                    self.recognize(image)
                )

        return results

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path: str | Path,
    ):

        return self.recognize(
            image_path
        )