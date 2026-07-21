"""
recognition/validator.py

SMILES validation utilities.
"""

from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.MolStandardize import rdMolStandardize


class SmilesValidator:
    """
    Validates and standardizes SMILES strings.
    """

    def __init__(self):

        self.fragment_chooser = (
            rdMolStandardize.LargestFragmentChooser()
        )

    # ---------------------------------------------------------

    @staticmethod
    def is_valid(smiles: str | None) -> bool:

        if not smiles:
            return False

        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False

    # ---------------------------------------------------------

    def largest_fragment(
        self,
        smiles: str,
    ) -> str | None:

        try:

            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            mol = self.fragment_chooser.choose(mol)

            return Chem.MolToSmiles(
                mol,
                canonical=True,
            )

        except Exception:

            return None

    # ---------------------------------------------------------

    @staticmethod
    def canonicalize(
        smiles: str,
    ) -> str | None:

        try:

            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            return Chem.MolToSmiles(
                mol,
                canonical=True,
            )

        except Exception:

            return None

    # ---------------------------------------------------------

    @staticmethod
    def molecular_formula(
        smiles: str,
    ) -> str | None:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return rdMolDescriptors.CalcMolFormula(
            mol
        )

    # ---------------------------------------------------------

    @staticmethod
    def molecular_weight(
        smiles: str,
    ) -> float | None:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return round(
            Descriptors.MolWt(mol),
            3,
        )

    # ---------------------------------------------------------

    @staticmethod
    def heavy_atoms(
        smiles: str,
    ) -> int | None:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return mol.GetNumHeavyAtoms()

    # ---------------------------------------------------------

    @staticmethod
    def atom_count(
        smiles: str,
    ) -> int | None:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return mol.GetNumAtoms()

    # ---------------------------------------------------------

    def validate(
        self,
        smiles: str | None,
    ) -> dict:
        """
        Complete validation pipeline.
        """

        if not self.is_valid(smiles):

            return {

                "valid": False,

                "canonical_smiles": None,

                "formula": None,

                "molecular_weight": None,

                "heavy_atoms": None,

                "atom_count": None,

            }

        smiles = self.largest_fragment(smiles)

        smiles = self.canonicalize(smiles)

        return {

            "valid": True,

            "canonical_smiles": smiles,

            "formula": self.molecular_formula(smiles),

            "molecular_weight": self.molecular_weight(smiles),

            "heavy_atoms": self.heavy_atoms(smiles),

            "atom_count": self.atom_count(smiles),

        }

    # ---------------------------------------------------------

    def __call__(
        self,
        smiles: str | None,
    ) -> dict:

        return self.validate(smiles)