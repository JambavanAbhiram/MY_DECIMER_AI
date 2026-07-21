"""
recognition/result.py

Common result object returned by every recognition engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RecognitionResult:
    """
    Standard recognition result.

    This object is exchanged between recognition engines,
    selector, validator and the main recognizer.
    """

    # ---------------------------------------------------------
    # Engine Information
    # ---------------------------------------------------------

    engine: str

    # ---------------------------------------------------------
    # Recognition Output
    # ---------------------------------------------------------

    smiles: str | None = None

    confidence: float | None = None

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    valid: bool = False

    canonical_smiles: str | None = None

    formula: str | None = None

    molecular_weight: float | None = None

    heavy_atoms: int | None = None

    atom_count: int | None = None

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------

    @property
    def success(self) -> bool:
        """
        Returns True if a SMILES was recognized.
        """
        return self.smiles is not None

    # ---------------------------------------------------------

    @property
    def has_confidence(self) -> bool:
        """
        Returns True if confidence is available.
        """
        return self.confidence is not None

    # ---------------------------------------------------------

    def update_validation(
        self,
        validation: dict,
    ) -> None:
        """
        Update this result using validator output.
        """

        self.valid = validation.get(
            "valid",
            False,
        )

        self.canonical_smiles = validation.get(
            "canonical_smiles"
        )

        self.formula = validation.get(
            "formula"
        )

        self.molecular_weight = validation.get(
            "molecular_weight"
        )

        self.heavy_atoms = validation.get(
            "heavy_atoms"
        )

        self.atom_count = validation.get(
            "atom_count"
        )

    # ---------------------------------------------------------

    def as_dict(self) -> dict:
        """
        Convert to a serializable dictionary.
        """

        return {

            "engine": self.engine,

            "smiles": self.smiles,

            "confidence": self.confidence,

            "valid": self.valid,

            "canonical_smiles": self.canonical_smiles,

            "formula": self.formula,

            "molecular_weight": self.molecular_weight,

            "heavy_atoms": self.heavy_atoms,

            "atom_count": self.atom_count,

            "metadata": self.metadata,

        }

    # ---------------------------------------------------------

    def __bool__(self) -> bool:
        """
        Allows:

        if result:
            ...
        """

        return self.success

    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"RecognitionResult("
            f"engine={self.engine!r}, "
            f"smiles={self.smiles!r}, "
            f"confidence={self.confidence!r}, "
            f"valid={self.valid})"
        )