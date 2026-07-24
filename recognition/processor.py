"""
recognition/processor.py

Recognition processing pipeline.

Pipeline

Image
    │
    ▼
Recognizer
    │
    ▼
(Optional redraw/export)
    │
    ▼
Dictionary result
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from recognition.recognizer import ChemicalRecognizer


class RecognitionProcessor:
    """
    Main recognition interface used by pipeline.py.
    """

    def __init__(
        self,
        recognizer: ChemicalRecognizer | None = None,
    ):
        self.recognizer = recognizer or ChemicalRecognizer()

    # -------------------------------------------------------------

    def process_image(
        self,
        image_path,
        redraw_png=None,
        redraw_svg=None,
    ) -> Dict:
        """
        Parameters
        ----------
        image_path : Path | str

        redraw_png : optional
            Reserved for future RDKit redraw export.

        redraw_svg : optional
            Reserved for future SVG export.

        Returns
        -------
        dict

        {
            success,
            smiles,
            confidence,
            agreement,
            votes,
            trust,
            pubchem,
            needs_review,
            reason
        }
        """

        image_path = Path(image_path)

        result = self.recognizer.recognize(image_path)

        # ---------------------------------------------------------
        # Future RDKit redraw support
        # ---------------------------------------------------------

        if (
            result["success"]
            and redraw_png is not None
        ):
            try:
                self._generate_png(
                    result["smiles"],
                    redraw_png,
                )
            except Exception:
                pass

        if (
            result["success"]
            and redraw_svg is not None
        ):
            try:
                self._generate_svg(
                    result["smiles"],
                    redraw_svg,
                )
            except Exception:
                pass

        return result

    # -------------------------------------------------------------

    def process_batch(
        self,
        image_paths,
    ):

        results = []

        for image in image_paths:
            results.append(
                self.process_image(image)
            )

        return results

    # -------------------------------------------------------------

    @staticmethod
    def _generate_png(
        smiles,
        output_path,
    ):
        """
        Generate PNG redraw using RDKit.
        """

        try:
            import importlib

            rdkit = importlib.import_module("rdkit")
            Chem = importlib.import_module("rdkit.Chem")
            Draw = importlib.import_module("rdkit.Chem.Draw")
        except Exception:
            # RDKit not available
            return

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return

        image = Draw.MolToImage(
            mol,
            size=(800, 800),
        )

        image.save(output_path)

    # -------------------------------------------------------------

    @staticmethod
    def _generate_svg(
        smiles,
        output_path,
    ):
        """
        Generate SVG redraw using RDKit.
        """

        try:
            import importlib

            rdkit = importlib.import_module("rdkit")
            Chem = importlib.import_module("rdkit.Chem")
            rdMolDraw2D = importlib.import_module("rdkit.Chem.Draw.rdMolDraw2D")
        except Exception:
            # RDKit not available
            return

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return

        drawer = rdMolDraw2D.MolDraw2DSVG(
            800,
            800,
        )

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg = drawer.GetDrawingText()

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(svg)

    # -------------------------------------------------------------

    __call__ = process_image