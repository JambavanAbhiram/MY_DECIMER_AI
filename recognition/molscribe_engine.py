"""
recognition/molscribe_engine.py

MolScribe inference engine.
Gracefully disables itself if no checkpoint is available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image


class MolScribeEngine:
    def __init__(self, model_path: str | Path | None = None):
        self.model = None
        self.enabled = False

        try:
            from molscribe import MolScribe

            # Default checkpoint location
            if model_path is None:
                model_path = (
                    Path(__file__).resolve().parents[1]
                    / "models"
                    / "molscribe"
                    / "molscribe.pth"
                )

            model_path = Path(model_path)

            if not model_path.exists():
                print(
                    "[INFO] MolScribe checkpoint not found. "
                    "Running with DECIMER only."
                )
                return

            self.model = MolScribe(str(model_path))
            self.enabled = True

            print(
                f"[INFO] MolScribe loaded from:\n{model_path}"
            )

        except Exception as e:
            print(
                f"[INFO] MolScribe disabled: {e}"
            )

    # ---------------------------------------------------------

    def predict(self, image_path: str | Path) -> Dict:

        if not self.enabled:
            return {
                "engine": "MolScribe",
                "success": False,
                "smiles": "",
                "confidence": None,
                "error": "MolScribe disabled",
            }

        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "engine": "MolScribe",
                "success": False,
                "smiles": "",
                "confidence": None,
                "error": f"Image not found: {image_path}",
            }

        try:

            image = Image.open(image_path).convert("RGB")

            prediction = self.model.predict_image(image)

            smiles = prediction.get("smiles", "")

            confidence = (
                prediction.get("confidence")
                or prediction.get("score")
                or prediction.get("probability")
            )

            return {
                "engine": "MolScribe",
                "success": bool(smiles),
                "smiles": smiles.strip(),
                "confidence": confidence,
                "error": None,
            }

        except Exception as e:

            return {
                "engine": "MolScribe",
                "success": False,
                "smiles": "",
                "confidence": None,
                "error": str(e),
            }

    __call__ = predict