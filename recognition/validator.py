"""
recognition/validator.py

Validates and canonicalizes predicted SMILES.
"""

from __future__ import annotations

from typing import Dict

from rdkit import Chem

try:
    import pubchempy as pcp
    PUBCHEM_AVAILABLE = True
except Exception:
    PUBCHEM_AVAILABLE = False


class SmilesValidator:

    def __init__(
        self,
        use_pubchem: bool = True,
    ):
        self.use_pubchem = (
            use_pubchem and PUBCHEM_AVAILABLE
        )

    # -------------------------------------------------------------

    def validate(
        self,
        smiles: str,
    ) -> Dict:

        if not smiles:

            return self._failed(
                "Empty SMILES."
            )

        # ---------------------------------------------------------
        # RDKit
        # ---------------------------------------------------------

        try:

            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return self._failed(
                    "RDKit failed."
                )

            Chem.SanitizeMol(mol)

            canonical = Chem.MolToSmiles(
                mol,
                canonical=True,
            )

        except Exception as e:

            return self._failed(str(e))

        # ---------------------------------------------------------
        # PubChem
        # ---------------------------------------------------------

        pubchem = False

        if self.use_pubchem:

            try:

                compounds = pcp.get_compounds(
                    canonical,
                    namespace="smiles",
                )

                pubchem = len(compounds) > 0

            except Exception:

                pubchem = False

        # ---------------------------------------------------------
        # Trust score
        # ---------------------------------------------------------

        trust = self._compute_trust(
            rdkit_valid=True,
            pubchem=pubchem,
        )

        needs_review = (
            trust in (
                "LOW",
                "MEDIUM",
            )
        )

        return {

            "valid": True,

            "original_smiles": smiles,

            "canonical_smiles": canonical,

            "pubchem": pubchem,

            "trust": trust,

            "needs_review": needs_review,

            "reason": "",
        }

    # -------------------------------------------------------------

    def compare(
        self,
        smiles1: str,
        smiles2: str,
    ) -> bool:
        """
        Compare two SMILES after canonicalization.
        """

        r1 = self.validate(smiles1)
        r2 = self.validate(smiles2)

        if not r1["valid"]:
            return False

        if not r2["valid"]:
            return False

        return (
            r1["canonical_smiles"]
            ==
            r2["canonical_smiles"]
        )

    # -------------------------------------------------------------

    @staticmethod
    def _compute_trust(
        rdkit_valid,
        pubchem,
    ):

        if rdkit_valid and pubchem:
            return "HIGH"

        if rdkit_valid:
            return "MEDIUM"

        return "LOW"

    # -------------------------------------------------------------

    @staticmethod
    def _failed(reason):

        return {

            "valid": False,

            "original_smiles": "",

            "canonical_smiles": "",

            "pubchem": False,

            "trust": "LOW",

            "needs_review": True,

            "reason": reason,
        }

    # -------------------------------------------------------------

    __call__ = validate