from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional


class ConsensusEngine:
    """
    Performs consensus voting across multiple recognition
    variants.
    """

    def __init__(self, min_votes: int = 2):
        """
        Parameters
        ----------
        min_votes : int
            Minimum number of votes required before accepting
            a prediction.
        """
        self.min_votes = min_votes

    # ---------------------------------------------------------

    @staticmethod
    def _normalize(smiles: Optional[str]) -> Optional[str]:
        """
        Normalize prediction strings.

        Removes whitespace and ignores empty predictions.
        """

        if smiles is None:
            return None

        smiles = smiles.strip()

        if smiles == "":
            return None

        return smiles

    # ---------------------------------------------------------

    def vote(
        self,
        predictions: List[str],
    ) -> Dict:
        """
        Majority voting over predictions.

        Parameters
        ----------
        predictions : list[str]

        Returns
        -------
        dict
        """

        cleaned = []

        for prediction in predictions:

            prediction = self._normalize(prediction)

            if prediction:
                cleaned.append(prediction)

        if len(cleaned) == 0:

            return {
                "smiles": None,
                "votes": 0,
                "confidence": 0.0,
                "accepted": False,
                "ranking": {},
            }

        counts = Counter(cleaned)

        smiles, votes = counts.most_common(1)[0]

        confidence = votes / len(cleaned)

        return {
            "smiles": smiles,
            "votes": votes,
            "confidence": confidence,
            "accepted": votes >= self.min_votes,
            "ranking": dict(counts),
        }

    # ---------------------------------------------------------

    def vote_variants(
        self,
        predictions: Dict[str, str],
    ) -> Dict:
        """
        Majority voting using a dictionary of

        {
            variant_name : prediction
        }

        Returns
        -------
        dict
        """

        result = self.vote(
            list(predictions.values())
        )

        result["variant_predictions"] = predictions

        return result

    # ---------------------------------------------------------

    @staticmethod
    def confidence_label(confidence: float) -> str:
        """
        Human-readable confidence label.
        """

        if confidence >= 0.95:
            return "VERY_HIGH"

        if confidence >= 0.80:
            return "HIGH"

        if confidence >= 0.60:
            return "MEDIUM"

        if confidence >= 0.40:
            return "LOW"

        return "VERY_LOW"

    # ---------------------------------------------------------

    def summarize(
        self,
        predictions: Dict[str, str],
    ) -> Dict:
        """
        Complete consensus analysis.

        Returns
        -------
        {
            smiles,
            votes,
            confidence,
            confidence_label,
            accepted,
            ranking,
            variant_predictions
        }
        """

        result = self.vote_variants(predictions)

        result["confidence_label"] = self.confidence_label(
            result["confidence"]
        )

        return result