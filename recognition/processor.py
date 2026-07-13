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
        image_path: str | Path,
        redraw_png: str | Path,
        redraw_svg: str | Path,
    ):
        image_path = Path(image_path)
        redraw_png = Path(redraw_png)
        redraw_svg = Path(redraw_svg)

        print("=" * 70)
        print(f"Processing Image : {image_path.name}")
        print(f"Image Path       : {image_path}")
        print("=" * 70)

        # ---------------------------------------------------------
        # Recognition
        # ---------------------------------------------------------

        print("[1/4] Starting DECIMER recognition...")

        recognition = self.recognizer.predict(image_path)

        print("[1/4] DECIMER recognition completed.")

        if recognition["smiles"] is None:
            print("[FAILED] No SMILES recognized.\n")
            return {
                "success": False,
                "reason": "No SMILES recognized",
                "smiles": None,
                **recognition,
            }

        print(f"Predicted SMILES length : {len(recognition['smiles'])}")
        print(f"Confidence              : {recognition['confidence']}")

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------

        print("[2/4] Validating SMILES...")

        validation = self.validator.validate(
            recognition["smiles"]
        )

        print("[2/4] Validation completed.")

        if not validation["valid"]:
            print("[FAILED] Invalid SMILES.\n")
            return {
                "success": False,
                "reason": "Invalid SMILES",
                **recognition,
                **validation,
            }

        smiles = validation["canonical_smiles"]

        print("Canonical SMILES generated.")
        print(f"Formula          : {validation['formula']}")
        print(f"Molecular Weight : {validation['molecular_weight']}")

        # ---------------------------------------------------------
        # Redraw
        # ---------------------------------------------------------

        print("[3/4] Rendering molecule...")

        redraw = self.renderer.render(
            smiles,
            redraw_png,
            redraw_svg,
        )

        print("[3/4] Rendering completed.")

        # ---------------------------------------------------------
        # Final
        # ---------------------------------------------------------

        print("[4/4] Image processing completed successfully.\n")

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
            image_path,
            redraw_png,
            redraw_svg,
        )