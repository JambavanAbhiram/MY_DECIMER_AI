"""
recognition/__init__.py

Recognition package for the DECIMER Project.

This package provides a modular recognition framework capable of
running multiple chemical OCR engines (DECIMER, MolScribe, etc.),
validating their outputs using RDKit, and selecting the best
prediction through an ensemble strategy.
"""

from .recognizer import ChemicalRecognizer
from .result import RecognitionResult
from .exceptions import RecognitionError

__all__ = [
    "ChemicalRecognizer",
    "RecognitionResult",
    "RecognitionError",
]

__version__ = "2.0.0"