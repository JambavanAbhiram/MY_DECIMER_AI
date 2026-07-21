"""
recognition/processor.py

Compatibility processor for the new modular recognition package.

This class preserves the interface expected by the existing
pipeline while internally using the new recognition framework.
"""

from __future__ import annotations

from pathlib import Path

from .recognizer import ChemicalRecognizer
from .redraw import MoleculeRenderer


class ImageProcessor:
    """
    Compatibility wrapper.

    Existing pipeline:
        result = processor.process_image(...)

    continues to work unchanged.
    """

    def __init__(self):

        self.recognizer = ChemicalRecognizer()

        self.renderer = MoleculeRenderer()

    # ---------------------------------------------------------

    def process_image(
        self,
        image_path: str | Path,
        redraw_png: str | Path,
        redraw_svg: str | Path,
    ) -> dict:

        image_path = Path(image_path)

        redraw_png = Path(redraw_png)

        redraw_svg = Path(redraw_svg)

        result = self.recognizer.recognize(
            image_path
        )

        if not result.success:

            return {

                "success": False,

                "reason": "Recognition failed",

                "smiles": None,

                "confidence": result.confidence,

                "agreement": None,

                "votes": None,

                "trust": False,

                "pubchem": None,

                "needs_review": True,

                "formula": None,

                "molecular_weight": None,

                "heavy_atoms": None,

                "atom_count": None,

                "redraw_png": None,

                "redraw_svg": None,

                "predictions": [],

            }

        # -----------------------------------------------------
        # Draw canonical molecule
        # -----------------------------------------------------

        png = None
        svg = None

        if result.valid:

            redraw = self.renderer.render(

                result.canonical_smiles,

                redraw_png,

                redraw_svg,

            )

            png = redraw["png"]

            svg = redraw["svg"]

        return {

            "success": result.valid,

            "reason": "",

            "smiles": (
                result.canonical_smiles
                if result.valid
                else result.smiles
            ),

            "confidence": result.confidence,

            # Compatibility placeholders
            "agreement": None,

            "votes": None,

            "trust": result.valid,

            "pubchem": None,

            "needs_review": not result.valid,

            "formula": result.formula,

            "molecular_weight": result.molecular_weight,

            "heavy_atoms": result.heavy_atoms,

            "atom_count": result.atom_count,

            "redraw_png": png,

            "redraw_svg": svg,

            "predictions": [
                engine.as_dict()
                for engine in result.metadata.get(
                    "engines",
                    [],
                )
            ],

        }

    # ---------------------------------------------------------

    def process_folder(
        self,
        folder,
        redraw_png_folder,
        redraw_svg_folder,
    ):

        folder = Path(folder)

        redraw_png_folder = Path(
            redraw_png_folder
        )

        redraw_svg_folder = Path(
            redraw_svg_folder
        )

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

                results.append(

                    self.process_image(

                        image,

                        redraw_png_folder
                        / f"{image.stem}.png",

                        redraw_svg_folder
                        / f"{image.stem}.svg",

                    )

                )

        return results

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path,
        redraw_png,
        redraw_svg,
    ):

        return self.process_image(

            image_path,

            redraw_png,

            redraw_svg,

        )