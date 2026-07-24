"""
recognition/selector.py

Chooses the best prediction among multiple recognition engines.
"""

from __future__ import annotations

from typing import List, Dict


class RecognitionSelector:
    """
    Selects the best prediction from multiple OCR engines.

    Input:
        [
            {
                "engine": "DECIMER",
                "success": True,
                "smiles": "...",
                "confidence": 0.81,
                ...
            },
            {
                "engine": "MolScribe",
                "success": True,
                "smiles": "...",
                "confidence": 0.94,
                ...
            }
        ]
    """

    def __init__(self):
        pass

    # -------------------------------------------------------------

    def select(self, predictions: List[Dict]) -> Dict:
        """
        Select the best prediction.

        Returns
        -------
        dict
        """

        if not predictions:
            return self._failed("No predictions available.")

        # Keep only successful predictions
        valid = [
            p for p in predictions
            if p.get("success") and p.get("smiles")
        ]

        if not valid:
            return self._failed("No engine produced a valid prediction.")

        # ---------------------------------------------------------
        # Single successful engine
        # ---------------------------------------------------------

        if len(valid) == 1:

            p = valid[0]

            return {
                "success": True,
                "engine": p["engine"],
                "smiles": p["smiles"],
                "confidence": p.get("confidence"),
                "agreement": False,
                "votes": 1,
            }

        # ---------------------------------------------------------
        # Multiple successful engines
        # ---------------------------------------------------------

        smiles_set = {
            p["smiles"].strip()
            for p in valid
        }

        # ---------------------------------------------------------
        # Everyone agrees
        # ---------------------------------------------------------

        if len(smiles_set) == 1:

            best = max(
                valid,
                key=lambda x: x.get("confidence") or 0
            )

            return {
                "success": True,
                "engine": best["engine"],
                "smiles": best["smiles"],
                "confidence": best.get("confidence"),
                "agreement": True,
                "votes": len(valid),
            }

        # ---------------------------------------------------------
        # Engines disagree
        # ---------------------------------------------------------

        best = max(
            valid,
            key=lambda x: x.get("confidence") or 0
        )

        return {
            "success": True,
            "engine": best["engine"],
            "smiles": best["smiles"],
            "confidence": best.get("confidence"),
            "agreement": False,
            "votes": len(valid),
        }

    # -------------------------------------------------------------

    @staticmethod
    def _failed(reason: str) -> Dict:

        return {
            "success": False,
            "engine": None,
            "smiles": "",
            "confidence": None,
            "agreement": False,
            "votes": 0,
            "reason": reason,
        }