from pathlib import Path
from typing import Optional

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D


class MoleculeRenderer:
    """
    Generates molecule depictions from SMILES.
    """

    def __init__(
        self,
        image_size=(800, 800),
    ):
        self.image_size = image_size

    # ---------------------------------------------------------

    @staticmethod
    def _molecule(smiles: str) -> Optional[Chem.Mol]:
        """
        Convert SMILES to RDKit Mol.
        """

        try:
            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            Chem.Compute2DCoords(mol)

            return mol

        except Exception:
            return None

    # ---------------------------------------------------------

    def to_png(
        self,
        smiles: str,
        output_path: Path,
    ) -> Optional[Path]:
        """
        Render molecule to PNG.
        """

        mol = self._molecule(smiles)

        if mol is None:
            return None

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image = Draw.MolToImage(
            mol,
            size=self.image_size,
        )

        image.save(output_path)

        return output_path

    # ---------------------------------------------------------

    def to_svg(
        self,
        smiles: str,
        output_path: Path,
    ) -> Optional[Path]:
        """
        Render molecule to SVG.
        """

        mol = self._molecule(smiles)

        if mol is None:
            return None

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        drawer = rdMolDraw2D.MolDraw2DSVG(
            self.image_size[0],
            self.image_size[1],
        )

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg = drawer.GetDrawingText()

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(svg)

        return output_path

    # ---------------------------------------------------------

    def render(
        self,
        smiles: str,
        png_path: Path,
        svg_path: Path,
    ) -> dict:
        """
        Generate both PNG and SVG.

        Returns
        -------
        dict
        """

        png = self.to_png(
            smiles,
            png_path,
        )

        svg = self.to_svg(
            smiles,
            svg_path,
        )

        return {

            "png": str(png) if png else None,

            "svg": str(svg) if svg else None,

            "success": png is not None and svg is not None,

        }

    # ---------------------------------------------------------

    def __call__(
        self,
        smiles: str,
        png_path: Path,
        svg_path: Path,
    ) -> dict:
        """
        Allows direct invocation.

        Example
        -------
        renderer(smiles, png_path, svg_path)
        """

        return self.render(
            smiles,
            png_path,
            svg_path,
        )