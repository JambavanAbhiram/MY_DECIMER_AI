"""
recognition/selector.py
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .result import RecognitionResult


class RecognitionSelector:
    """Select the best recognition result from multiple engines."""

    def __init__(self, min_votes: int = 2):
        self.min_votes = min_votes

    @staticmethod
    def _valid(results: Iterable[RecognitionResult]):
        return [r for r in results if r.smiles]

    @staticmethod
    def _confidence(result: RecognitionResult) -> float:
        return float(result.confidence or 0.0)

    def majority_vote(self, results):
        smiles = [r.smiles for r in results if r.smiles]
        if not smiles:
            return None, 0

        votes = Counter(smiles)
        winner, count = votes.most_common(1)[0]
        return winner, count

    def select(self, results):
        results = self._valid(results)

        if not results:
            return RecognitionResult(
                engine="NONE",
                smiles=None,
                confidence=None,
                metadata={
                    "reason": "No valid predictions",
                    "selection": "none",
                },
            )

        winner, count = self.majority_vote(results)

        if winner is not None and count >= self.min_votes:
            candidates = [r for r in results if r.smiles == winner]
            best = max(candidates, key=self._confidence)
            best.metadata.update({
                "selection": "majority_vote",
                "votes": count,
                "winner": winner,
            })
            return best

        best = max(results, key=self._confidence)

        best.metadata.update({
            "selection": "highest_confidence",
            "votes": 1,
            "winner": best.smiles,
        })

        return best

    def __call__(self, results):
        return self.select(results)
