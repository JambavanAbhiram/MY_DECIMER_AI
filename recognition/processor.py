"""
recognition/processor.py

Recognition processor for the DECIMER pipeline.

Pipeline
--------
Cleaned Image
        ↓
Recognition
        ↓
Validation
        ↓
Redraw
"""

from pathlib import Path

from .recognizer import DecimerRecognizer
from .validator import SmilesValidator
from .redraw import MoleculeRenderer


class ImageProcessor:
    def __init__(self):
        self.recognizer = DecimerRecognizer()
        self.validator = SmilesValidator()
        self.renderer = MoleculeRenderer()

    def process_image(
        self,
        image_path: str | Path | None = None,
        redraw_png: str | Path | None = None,
        redraw_svg: str | Path | None = None,
        cleaned_path: str | Path | None = None,
    ):
        # Allow cleaned_path as an alias for image_path
        if cleaned_path is not None:
            image_path = cleaned_path

        if image_path is None:
            raise ValueError("Either image_path or cleaned_path must be provided.")

        if redraw_png is None or redraw_svg is None:
            raise ValueError("redraw_png and redraw_svg must be provided.")

        image_path = Path(image_path)
        redraw_png = Path(redraw_png)
        redraw_svg = Path(redraw_svg)

        recognition = self.recognizer.predict(image_path)

        if recognition["smiles"] is None:
            return {
                "success": False,
                "reason": "No SMILES recognized",
                "smiles": None,
                **recognition,
            }

        validation = self.validator.validate(recognition["smiles"])

        if not validation["valid"]:
            return {
                "success": False,
                "reason": "Invalid SMILES",
                **recognition,
                **validation,
            }

        smiles = validation["canonical_smiles"]

        redraw = self.renderer.render(
            smiles,
            redraw_png,
            redraw_svg,
        )

        return {
            "success": True,
            "reason": "",
            "smiles": smiles,
            "confidence": recognition["confidence"],
            "agreement": recognition["agreement"],
            "votes": recognition["votes"],
            "trust": recognition["trust"],
            "pubchem": recognition["pubchem"],
            "needs_review": recognition["needs_review"],
            "formula": validation["formula"],
            "molecular_weight": validation["molecular_weight"],
            "heavy_atoms": validation["heavy_atoms"],
            "atom_count": validation["atom_count"],
            "redraw_png": redraw["png"],
            "redraw_svg": redraw["svg"],
            "predictions": recognition["predictions"],
        }

    def process_folder(
        self,
        folder,
        redraw_png_folder,
        redraw_svg_folder,
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
            if image.is_file() and image.suffix.lower() in extensions:
                result = self.process_image(
                    image,
                    redraw_png_folder / f"{image.stem}.png",
                    redraw_svg_folder / f"{image.stem}.svg",
                )
                results.append(result)

        return results

    def __call__(
        self,
        image_path,
        redraw_png,
        redraw_svg,
    ):
        return self.process_image(
            image_path=image_path,
            redraw_png=redraw_png,
            redraw_svg=redraw_svg,
        )