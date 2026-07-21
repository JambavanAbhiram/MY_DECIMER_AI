"""
recognition/exceptions.py

Custom exceptions for the recognition package.
"""

from __future__ import annotations


class RecognitionError(Exception):
    """
    Base exception for all recognition-related errors.
    """

    pass


# ------------------------------------------------------------------


class EngineLoadError(RecognitionError):
    """
    Raised when a recognition engine cannot be initialized.
    """

    pass


# ------------------------------------------------------------------


class RecognitionEngineError(RecognitionError):
    """
    Raised when a recognition engine fails during inference.
    """

    pass


# ------------------------------------------------------------------


class ModelNotLoadedError(RecognitionError):
    """
    Raised when inference is attempted before loading a model.
    """

    pass


# ------------------------------------------------------------------


class InvalidImageError(RecognitionError):
    """
    Raised when an image is missing, unreadable,
    or has an unsupported format.
    """

    pass


# ------------------------------------------------------------------


class RecognitionFailedError(RecognitionError):
    """
    Raised when no recognition engine produces
    a usable SMILES prediction.
    """

    pass


# ------------------------------------------------------------------


class InvalidSmilesError(RecognitionError):
    """
    Raised when a predicted SMILES cannot be parsed
    by RDKit.
    """

    pass


# ------------------------------------------------------------------


class ValidationError(RecognitionError):
    """
    Raised when SMILES validation fails.
    """

    pass


# ------------------------------------------------------------------


class SelectorError(RecognitionError):
    """
    Raised when the selector cannot determine
    the best recognition result.
    """

    pass