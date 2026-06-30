from __future__ import annotations

from typing import Dict, Optional

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors


class SmilesValidator:
    """
    Validates and standardizes SMILES strings.
    """

    # ---------------------------------------------------------

    @staticmethod
    def is_valid(smiles: Optional[str]) -> bool:
        """
        Returns True if RDKit can parse the SMILES.
        """

        if smiles is None:
            return False

        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False

    # ---------------------------------------------------------

    @staticmethod
    def canonicalize(smiles: str) -> Optional[str]:
        """
        Convert SMILES into canonical representation.
        """

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
    def largest_fragment(smiles: str) -> Optional[str]:
        """
        Keep only the largest fragment.

        Example

        Na.Cl.CCO

        ↓

        CCO
        """

        try:

            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            frags = Chem.GetMolFrags(
                mol,
                asMols=True,
            )

            if len(frags) == 0:
                return None

            largest = max(
                frags,
                key=lambda x: x.GetNumAtoms(),
            )

            return Chem.MolToSmiles(
                largest,
                canonical=True,
            )

        except Exception:

            return None

    # ---------------------------------------------------------

    @staticmethod
    def molecular_formula(smiles: str) -> Optional[str]:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return rdMolDescriptors.CalcMolFormula(
            mol
        )

    # ---------------------------------------------------------

    @staticmethod
    def molecular_weight(smiles: str) -> Optional[float]:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return round(
            Descriptors.MolWt(mol),
            3,
        )

    # ---------------------------------------------------------

    @staticmethod
    def heavy_atoms(smiles: str) -> Optional[int]:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return mol.GetNumHeavyAtoms()

    # ---------------------------------------------------------

    @staticmethod
    def atom_count(smiles: str) -> Optional[int]:

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        return mol.GetNumAtoms()

    # ---------------------------------------------------------

    def validate(
        self,
        smiles: str,
    ) -> Dict:
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