"""
hashing.py

Document ID Generation

Responsibilities
----------------
1. Generate deterministic document IDs.
2. Compute SHA-256 hashes for PDF files.
3. Support hashing from both file paths and PDF blobs.

Author: Abhiram
"""

from pathlib import Path
import hashlib


CHUNK_SIZE = 1024 * 1024  # 1 MB


def sha256_from_file(pdf_path):
    """
    Compute SHA-256 hash of a PDF file.

    Parameters
    ----------
    pdf_path : str | Path

    Returns
    -------
    str
        Hexadecimal SHA-256 hash.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    hasher = hashlib.sha256()

    with open(pdf_path, "rb") as file:

        while True:

            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def sha256_from_bytes(pdf_bytes):
    """
    Compute SHA-256 hash of a PDF blob.

    Parameters
    ----------
    pdf_bytes : bytes

    Returns
    -------
    str
    """

    hasher = hashlib.sha256()

    hasher.update(pdf_bytes)

    return hasher.hexdigest()


def generate_document_id(input_data):
    """
    Generate a document ID from either

        • PDF Path
        • PDF Blob

    Parameters
    ----------
    input_data
        Path | str | bytes

    Returns
    -------
    str
        SHA-256 document ID.
    """

    if isinstance(input_data, bytes):

        return sha256_from_bytes(input_data)

    elif isinstance(input_data, (str, Path)):

        return sha256_from_file(input_data)

    else:

        raise TypeError(
            "Input must be a PDF path or PDF bytes."
        )