"""
recognition/molscribe_engine.py

MolScribe recognition engine.

This module wraps MolScribe and exposes a unified interface
compatible with the recognition framework.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import huggingface_hub

from molscribe import MolScribe

from .base_engine import BaseRecognitionEngine
from .result import RecognitionResult


class MolScribeEngine(BaseRecognitionEngine):
    """
    Wrapper around MolScribe.

    The model is lazily loaded on the first prediction and
    reused for all subsequent predictions.
    """

    MODEL_REPO = "yujieq/MolScribe"
    MODEL_FILE = "swin_base_char_aux_1m.pth"

    def __init__(
        self,
        device: str = "cpu",
    ):
        super().__init__("MolScribe")

        self.device = torch.device(device)
        self.model = None

    # ---------------------------------------------------------

    def load(self) -> None:
        """
        Load the MolScribe model.
        """

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

    # ---------------------------------------------------------

    def recognize(
        self,
        image_path: Path,
    ) -> RecognitionResult:

        self.ensure_loaded()

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        try:

            prediction = self.model.predict_image_file(
                str(image_path)
            )

            smiles = prediction.get("smiles")

            confidence = prediction.get("confidence")

            if confidence is not None:
                confidence = float(confidence)

            return RecognitionResult(

                engine=self.name,

                smiles=smiles,

                confidence=confidence,

                metadata={
                    "device": str(self.device),
                },

            )

        except Exception as exc:

            return RecognitionResult(

                engine=self.name,

                smiles=None,

                confidence=None,

                metadata={
                    "error": str(exc),
                },

            )

    # ---------------------------------------------------------

    def unload(self) -> None:
        """
        Release model resources.
        """

        self.model = None
        self._loaded = False

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path: Path,
    ) -> RecognitionResult:

        return self.recognize(image_path)