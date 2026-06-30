"""
core/hashing.py

Utility functions for generating cryptographic hashes.

Currently used for:
    - Duplicate PDF detection
    - Document identification
    - Integrity verification

Author: DECIMER Pipeline
"""

from pathlib import Path
import hashlib

class HashManager:
    """
    Handles hashing operations for project files.
    """

    CHUNK_SIZE = 8192

    @staticmethod
    def sha256(file_path: Path) -> str:
        """
        Compute the SHA256 hash of a file.

        Parameters
        ----------
        file_path : Path
            Path to the file.

        Returns
        -------
        str
            SHA256 hexadecimal digest.
        """
        hasher = hashlib.sha256()

        with open(file_path, "rb") as file:
            while chunk := file.read(HashManager.CHUNK_SIZE):
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def md5(file_path: Path) -> str:
        """
        Compute the MD5 hash of a file.

        Useful for quick comparisons.
        Not recommended for security.
        """
        hasher = hashlib.md5()

        with open(file_path, "rb") as file:
            while chunk := file.read(HashManager.CHUNK_SIZE):
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def verify(file_path: Path, expected_hash: str) -> bool:
        """
        Verify a SHA256 hash.

        Parameters
        ----------
        file_path : Path
            File to verify.

        expected_hash : str
            Expected SHA256 hash.

        Returns
        -------
        bool
        """
        return HashManager.sha256(file_path) == expected_hash