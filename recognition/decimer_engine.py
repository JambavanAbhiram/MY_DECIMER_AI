"""
recognition/decimer_engine.py

DECIMER inference engine.

Responsibilities:
- Load DECIMER Image Transformer once.
- Predict SMILES from an image.
- Return prediction and confidence (if available).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image

try:
    from DECIMER import predict_SMILES
except ImportError as e:
    raise ImportError(
        "DECIMER is not installed.\n"
        "Install using:\n"
        "pip install decimer"
    ) from e


class DECIMEREngine:
    """
    Wrapper around DECIMER Image Transformer.
    """

    def __init__(self):
        pass

    def predict(self, image_path: str | Path) -> Dict:
        """
        Run DECIMER on an image.

        Parameters
        ----------
        image_path : str | Path

        Returns
        -------
        dict
        {
            "engine": "DECIMER",
            "success": bool,
            "smiles": str,
            "confidence": float | None,
            "error": str | None
        }
        """

        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "engine": "DECIMER",
                "success": False,
                "smiles": "",
                "confidence": None,
                "error": f"Image not found: {image_path}",
            }

        try:
            smiles = predict_SMILES(str(image_path))

            return {
                "engine": "DECIMER",
                "success": bool(smiles),
                "smiles": smiles.strip() if smiles else "",
                "confidence": None,
                "error": None,
            }

        except Exception as e:
            return {
                "engine": "DECIMER",
                "success": False,
                "smiles": "",
                "confidence": None,
                "error": str(e),
            }

    __call__ = predict