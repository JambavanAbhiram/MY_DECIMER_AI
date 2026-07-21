"""
utils.py

Common utility functions for the DECIMER Evaluation Framework.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from rdkit import Chem


# =========================================================
# SMILES Utilities
# =========================================================

def canonicalize_smiles(smiles: str | None) -> str | None:
    """
    Convert a SMILES string to its canonical representation.

    Parameters
    ----------
    smiles : str | None

    Returns
    -------
    str | None
        Canonical SMILES if valid, otherwise None.
    """

    if pd.isna(smiles):
        return None

    smiles = str(smiles).strip()

    if smiles == "":
        return None

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


def is_valid_smiles(smiles: str | None) -> bool:
    """
    Check whether a SMILES string is valid.
    """

    return canonicalize_smiles(smiles) is not None


# =========================================================
# File Utilities
# =========================================================

def file_exists(path: str | Path) -> bool:
    """
    Check whether a file exists.
    """

    return Path(path).exists()


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory if it doesn't exist.
    """

    path = Path(path)

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path