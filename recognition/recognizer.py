"""
recognition/recognizer.py

Hybrid chemical structure recognizer.

Pipeline
--------
Image
   │
   ├── DECIMER
   ├── MolScribe
   │
   ▼
Selector
   │
   ▼
Validator
   │
   ▼
Final prediction
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .decimer_engine import DECIMEREngine
from .molscribe_engine import MolScribeEngine
from .selector import RecognitionSelector
from .validator import SmilesValidator


class ChemicalRecognizer:
    """
    Hybrid recognizer combining DECIMER and MolScribe.
    """

    def __init__(
        self,
        decimer_engine: DECIMEREngine | None = None,
        molscribe_engine: MolScribeEngine | None = None,
        selector: RecognitionSelector | None = None,
        validator: SmilesValidator | None = None,
    ):

        self.decimer = decimer_engine or DECIMEREngine()
        self.molscribe = molscribe_engine or MolScribeEngine()

        self.selector = selector or RecognitionSelector()
        self.validator = validator or SmilesValidator()

    # -------------------------------------------------------------

    def recognize(
        self,
        image_path: str | Path,
    ) -> Dict:

        image_path = Path(image_path)

        predictions: List[Dict] = []

        # ---------------------------------------------------------
        # DECIMER
        # ---------------------------------------------------------

        try:
            decimer = self.decimer.predict(image_path)
            predictions.append(decimer)

        except Exception as e:

            predictions.append(
                {
                    "engine": "DECIMER",
                    "success": False,
                    "smiles": "",
                    "confidence": None,
                    "error": str(e),
                }
            )

        # ---------------------------------------------------------
        # MolScribe
        # ---------------------------------------------------------

        try:
            molscribe = self.molscribe.predict(image_path)
            predictions.append(molscribe)

        except Exception as e:

            predictions.append(
                {
                    "engine": "MolScribe",
                    "success": False,
                    "smiles": "",
                    "confidence": None,
                    "error": str(e),
                }
            )

        # ---------------------------------------------------------
        # Select best prediction
        # ---------------------------------------------------------

        best = self.selector.select(predictions)

        if not best["success"]:

            return {

                "success": False,

                "smiles": "",

                "confidence": None,

                "agreement": False,

                "votes": 0,

                "trust": "LOW",

                "pubchem": False,

                "needs_review": True,

                "reason": best.get(
                    "reason",
                    "No prediction.",
                ),
            }

        # ---------------------------------------------------------
        # Validate selected SMILES
        # ---------------------------------------------------------

        validation = self.validator.validate(
            best["smiles"]
        )

        if not validation["valid"]:

            return {

                "success": False,

                "smiles": "",

                "confidence": best.get(
                    "confidence"
                ),

                "agreement": best.get(
                    "agreement",
                    False,
                ),

                "votes": best.get(
                    "votes",
                    1,
                ),

                "trust": "LOW",

                "pubchem": False,

                "needs_review": True,

                "reason": validation[
                    "reason"
                ],
            }

        # ---------------------------------------------------------
        # Final output
        # ---------------------------------------------------------

        return {

            "success": True,

            "engine": best["engine"],

            "smiles": validation[
                "canonical_smiles"
            ],

            "confidence": best.get(
                "confidence"
            ),

            "agreement": best.get(
                "agreement",
                False,
            ),

            "votes": best.get(
                "votes",
                1,
            ),

            "trust": validation[
                "trust"
            ],

            "pubchem": validation[
                "pubchem"
            ],

            "needs_review": validation[
                "needs_review"
            ],

            "reason": "",
        }

    # -------------------------------------------------------------

    __call__ = recognize