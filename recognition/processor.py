"""
recognition/processor.py

Recognition processor for the DECIMER pipeline.

Pipeline
--------
Image
    ↓
Recognizer
    ↓
Validator
    ↓
Renderer
"""

from pathlib import Path
from typing import Dict

from .recognizer import DecimerRecognizer
from .validator import SmilesValidator
from .redraw import MoleculeRenderer


class RecognitionProcessor:

    def __init__(self):

        self.recognizer = DecimerRecognizer()

        self.validator = SmilesValidator()

        self.renderer = MoleculeRenderer()

    # ---------------------------------------------------------

    def process_image(
        self,
        image_path: str | Path,
        cleaned_path: str | Path,
        redraw_png: str | Path,
        redraw_svg: str | Path,
    ) -> Dict:

        image_path = Path(image_path)
        cleaned_path = Path(cleaned_path)
        redraw_png = Path(redraw_png)
        redraw_svg = Path(redraw_svg)

        # ---------------------------------------------------------
        # Recognition
        # ---------------------------------------------------------

        recognition = self.recognizer.predict(image_path)

        if recognition["smiles"] is None:

            return {

                "success": False,

                "reason": "No SMILES recognized",

                **recognition,

            }

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------

        validation = self.validator.validate(
            recognition["smiles"]
        )

        if not validation["valid"]:

            return {

                "success": False,

                "reason": "Invalid SMILES",

                **recognition,

                **validation,

            }

        smiles = validation["canonical_smiles"]

        # ---------------------------------------------------------
        # Redraw
        # ---------------------------------------------------------

        redraw = self.renderer.render(
            smiles,
            redraw_png,
            redraw_svg,
        )

        # ---------------------------------------------------------
        # Return
        # ---------------------------------------------------------

        return {

            "success": True,

            "smiles": smiles,

            "trust": recognition["trust"],

            "votes": recognition["votes"],

            "total_predictions": recognition["total"],

            "agreement": recognition["agreement"],

            "confidence": recognition["confidence"],

            "pubchem": recognition["pubchem"],

            "needs_review": recognition["needs_review"],

            "formula": validation["formula"],

            "molecular_weight": validation["molecular_weight"],

            "heavy_atoms": validation["heavy_atoms"],

            "atom_count": validation["atom_count"],

            "original_image": str(image_path),

            "cleaned_image": str(cleaned_path),

            "redraw_png": redraw["png"],

            "redraw_svg": redraw["svg"],

            "predictions": recognition["predictions"],

        }

    # ---------------------------------------------------------

    def process_folder(
        self,
        folder: str | Path,
        redraw_png_folder: str | Path,
        redraw_svg_folder: str | Path,
    ):

        folder = Path(folder)

        redraw_png_folder = Path(redraw_png_folder)

        redraw_svg_folder = Path(redraw_svg_folder)

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

                result = self.process_image(

                    image,

                    "",

                    redraw_png_folder / f"{image.stem}.png",

                    redraw_svg_folder / f"{image.stem}.svg",

                )

                results.append(result)

        return results

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path,
        cleaned_path,
        redraw_png,
        redraw_svg,
    ):

        return self.process_image(
            image_path,
            cleaned_path,
            redraw_png,
            redraw_svg,
        )