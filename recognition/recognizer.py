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
from .result import RecognitionResult


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

    def _run_engines(
        self,
        image_path: Path,
    ):
        """
        Executes every recognition engine independently.

        One engine crashing should never stop
        the remaining engines.
        """

        engine_results = []
        failed_engines = []

        for engine in self.engines:

            try:

                result = engine.recognize(
                    image_path
                )

                engine_results.append(result)

            except Exception as exc:

                failed_engines.append({

                    "engine": engine.name,

                    "error": str(exc),

                })

        return engine_results, failed_engines

    # ---------------------------------------------------------

    def recognize(
        self,
        image_path: str | Path,
    ):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        engine_results, failed_engines = self._run_engines(
            image_path
        )

        # ---------------------------------------------
        # Every engine failed
        # ---------------------------------------------

        if not engine_results:

            return RecognitionResult(

                engine="NONE",

                smiles=None,

                confidence=None,

                metadata={

                    "valid": False,

                    "reason": "All recognition engines failed",

                    "engine_errors": failed_engines,

                },

            )

        # ---------------------------------------------
        # Select best prediction
        # ---------------------------------------------

        selected = self.selector.select(
            engine_results
        )

                # ---------------------------------------------
        # Nothing recognized
        # ---------------------------------------------

        if selected.smiles is None:

            selected.valid = False

            selected.metadata.update({

                "valid": False,

                "engines": engine_results,

                "engine_errors": failed_engines,

            })

            return selected

        # ---------------------------------------------
        # Validate SMILES
        # ---------------------------------------------

        validation = self.validator.validate(
            selected.smiles
        )

        selected.update_validation(
            validation
        )

        selected.metadata.update(validation)

        selected.metadata["engines"] = engine_results

        selected.metadata["engine_errors"] = (
            failed_engines
        )

        # ---------------------------------------------
        # Canonicalize if valid
        # ---------------------------------------------

        if selected.valid:

            selected.smiles = (
                selected.canonical_smiles
            )

            selected.metadata[
                "recognition_status"
            ] = "VALID"

        else:

            selected.metadata[
                "recognition_status"
            ] = "INVALID"

        # ---------------------------------------------
        # Recognition statistics
        # ---------------------------------------------

        selected.metadata["total_engines"] = len(
            self.engines
        )

        selected.metadata[
            "successful_engines"
        ] = len(engine_results)

        selected.metadata[
            "failed_engine_count"
        ] = len(failed_engines)

        selected.metadata[
            "successful_engine_names"
        ] = [
            result.engine
            for result in engine_results
        ]

        selected.metadata[
            "failed_engine_names"
        ] = [
            engine["engine"]
            for engine in failed_engines
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
                and image.suffix.lower()
                in extensions
            ):

                try:

                    result = self.recognize(
                        image
                    )

                    results.append(result)

                except Exception as exc:

                    results.append(

                        RecognitionResult(

                            engine="PIPELINE",

                            smiles=None,

                            confidence=None,

                            metadata={

                                "valid": False,

                                "image": str(image),

                                "error": str(exc),

                            },

                        )

                    )

                    return results

    # ---------------------------------------------------------

    def available_engines(
        self,
    ) -> list[str]:
        """
        Returns the names of all configured
        recognition engines.
        """

        return [
            engine.name
            for engine in self.engines
        ]

    # ---------------------------------------------------------

    def engine_count(
        self,
    ) -> int:
        """
        Returns the number of configured engines.
        """

        return len(self.engines)

    # ---------------------------------------------------------

    def unload_models(
        self,
    ) -> None:
        """
        Releases resources used by all
        recognition engines.

        Useful when running very large batches
        or when explicitly freeing GPU memory.
        """

        for engine in self.engines:

            try:

                engine.unload()

            except Exception:

                pass

    # ---------------------------------------------------------

    def reload_models(
        self,
    ) -> None:
        """
        Reload every configured engine.
        """

        self.unload_models()

        for engine in self.engines:

            try:

                engine.ensure_loaded()

            except Exception:

                pass

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path: str | Path,
    ):
        """
        Allows direct invocation.

        Example
        -------
        recognizer(image_path)
        """

        return self.recognize(
            image_path
        )