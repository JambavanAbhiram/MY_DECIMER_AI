"""
recognition/result.py

Recognition result models.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Dict


@dataclass
class RecognitionResult:
    """
    Standard recognition result.
    """

    success: bool

    engine: Optional[str] = None

    smiles: str = ""

    confidence: Optional[float] = None

    agreement: bool = False

    votes: int = 0

    trust: str = "LOW"

    pubchem: bool = False

    needs_review: bool = True

    reason: str = ""

    # ---------------------------------------------------------

    def to_dict(self) -> Dict:
        """
        Convert to dictionary expected by pipeline.py.
        """
        return asdict(self)

    # ---------------------------------------------------------

    @classmethod
    def failure(
        cls,
        reason: str,
    ) -> "RecognitionResult":

        return cls(
            success=False,
            reason=reason,
        )

    # ---------------------------------------------------------

    @classmethod
    def success_result(
        cls,
        engine: str,
        smiles: str,
        confidence: float | None = None,
        agreement: bool = False,
        votes: int = 1,
        trust: str = "MEDIUM",
        pubchem: bool = False,
        needs_review: bool = False,
    ) -> "RecognitionResult":

        return cls(
            success=True,
            engine=engine,
            smiles=smiles,
            confidence=confidence,
            agreement=agreement,
            votes=votes,
            trust=trust,
            pubchem=pubchem,
            needs_review=needs_review,
        )