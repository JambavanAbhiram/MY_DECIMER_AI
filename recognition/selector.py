"""
recognition/selector.py

Selects the best recognition result from multiple OCR engines.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Optional

from .result import RecognitionResult


class RecognitionSelector:
    """
    Select the best prediction from multiple recognition engines.

    Selection priority
    ------------------
    1. Majority vote
    2. Highest confidence
    3. First valid prediction
    """

    def __init__(
        self,
        min_votes: int = 2,
    ):
        self.min_votes = min_votes

    # ---------------------------------------------------------

    @staticmethod
    def _valid(
        results: Iterable[RecognitionResult],
    ) -> List[RecognitionResult]:

        return [
            result
            for result in results
            if result.smiles
        ]

    # ---------------------------------------------------------

    @staticmethod
    def _confidence(
        result: RecognitionResult,
    ) -> float:

        return (
            result.confidence
            if result.confidence is not None
            else 0.0
        )

    # ---------------------------------------------------------

    def majority_vote(
        self,
        results: List[RecognitionResult],
    ) -> Optional[str]:

        smiles = [
            result.smiles
            for result in results
            if result.smiles
        ]

        if not smiles:
            return None

        votes = Counter(smiles)

        winner, count = votes.most_common(1)[0]

        if count >= self.min_votes:
            return winner

        return None

    # ---------------------------------------------------------

    def highest_confidence(
        self,
        results: List[RecognitionResult],
    ) -> Optional[RecognitionResult]:

        if not results:
            return None

        return max(
            results,
            key=self._confidence,
        )

    # ---------------------------------------------------------

    def select(
        self,
        results: List[RecognitionResult],
    ) -> RecognitionResult:
        """
        Select the best recognition result.

        Returns
        -------
        RecognitionResult
        """

        results = self._valid(results)

        if not results:

            return RecognitionResult(
                engine="NONE",
                smiles=None,
                confidence=None,
                metadata={
                    "reason": "No valid predictions"
                },
            )

        # -------------------------------------------------
        # Majority voting
        # -------------------------------------------------

        winner = self.majority_vote(results)

        if winner is not None:

            candidates = [
                result
                for result in results
                if result.smiles == winner
            ]

            best = self.highest_confidence(
                candidates
            )

            best.metadata["selection"] = "majority_vote"

            return best

        # -------------------------------------------------
        # Highest confidence
        # -------------------------------------------------

        best = self.highest_confidence(
            results
        )

        best.metadata["selection"] = "highest_confidence"

        return best

    # ---------------------------------------------------------

    def __call__(
        self,
        results: List[RecognitionResult],
    ) -> RecognitionResult:

        return self.select(results)