"""
recognition/decimer_engine.py

DECIMER recognition engine.

This module wraps the DECIMER Image Transformer and exposes a
consistent interface for the recognition pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from .base_engine import BaseRecognitionEngine
from .result import RecognitionResult


class DecimerEngine(BaseRecognitionEngine):
    """
    Wrapper around DECIMER Image Transformer.

    Supports:
    - confidence output (if available)
    - handwritten mode
    - graceful fallback across DECIMER versions
    """

    def __init__(
        self,
        hand_drawn: bool = False,
    ):
        super().__init__("DECIMER")

        self.hand_drawn = hand_drawn
        self.predict_fn = None

    # ---------------------------------------------------------

    def load(self) -> None:
        """
        Import DECIMER only once.
        """

        if self.loaded:
            return

        from DECIMER import predict_SMILES

        self.predict_fn = predict_SMILES

        self._loaded = True

    # ---------------------------------------------------------

    def _call_decimer(
        self,
        image_path: Path,
    ) -> tuple[Optional[str], Optional[float]]:
        """
        Calls DECIMER while supporting multiple API versions.
        """

        kwargs_list = [

            {
                "confidence": True,
                "hand_drawn": self.hand_drawn,
            },

            {
                "confidence": True,
            },

            {
                "hand_drawn": self.hand_drawn,
            },

            {},

        ]

        for kwargs in kwargs_list:

            try:

                result = self.predict_fn(
                    str(image_path),
                    **kwargs,
                )

                # Newer DECIMER versions
                if isinstance(result, tuple):

                    smiles = result[0]

                    confidence = None

                    try:

                        confidence = float(
                            np.mean(
                                [
                                    token[1]
                                    for token in result[1]
                                ]
                            )
                        )

                    except Exception:
                        pass

                    return smiles, confidence

                # Older DECIMER versions

                return result, None

            except TypeError:

                continue

            except Exception:

                continue

        return None, None

    # ---------------------------------------------------------

    def recognize(
        self,
        image_path: Path,
    ) -> RecognitionResult:

        self.ensure_loaded()

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        smiles, confidence = self._call_decimer(
            image_path
        )

        return RecognitionResult(

            engine=self.name,

            smiles=smiles,

            confidence=confidence,

            metadata={
                "hand_drawn": self.hand_drawn,
            },

        )

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path: Path,
    ) -> RecognitionResult:

        return self.recognize(image_path)