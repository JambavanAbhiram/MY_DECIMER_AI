"""
recognition/molscribe_engine.py
"""

from __future__ import annotations

from pathlib import Path

import torch
import huggingface_hub
from molscribe import MolScribe

from .base_engine import BaseRecognitionEngine
from .result import RecognitionResult


class MolScribeEngine(BaseRecognitionEngine):
    MODEL_REPO = "yujieq/MolScribe"
    MODEL_FILE = "swin_base_char_aux_1m.pth"

    def __init__(self, device: str | None = None):
        super().__init__("MolScribe")
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model = None

    def load(self) -> None:
        if self.loaded:
            return

        checkpoint = huggingface_hub.hf_hub_download(
            repo_id=self.MODEL_REPO,
            filename=self.MODEL_FILE,
        )

        self.model = MolScribe(
            checkpoint,
            device=self.device,
        )
        self._loaded = True

    def recognize(self, image_path: Path) -> RecognitionResult:
        self.ensure_loaded()

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        metadata = {
            "device": str(self.device),
        }

        try:
            prediction = self.model.predict_image_file(
                str(image_path)
            )

            smiles = prediction.get("smiles")

            confidence = prediction.get("confidence")
            if confidence is not None:
                confidence = float(confidence)

            metadata["raw_prediction"] = prediction

            return RecognitionResult(
                engine=self.name,
                smiles=smiles,
                confidence=confidence,
                metadata=metadata,
            )

        except Exception as exc:
            metadata["error"] = str(exc)

            return RecognitionResult(
                engine=self.name,
                smiles=None,
                confidence=None,
                metadata=metadata,
            )

    def unload(self) -> None:
        self.model = None
        self._loaded = False

    def __call__(self, image_path: Path) -> RecognitionResult:
        return self.recognize(image_path)
