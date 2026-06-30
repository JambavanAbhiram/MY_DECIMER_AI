"""
core/inventory.py

Scans PDF files, removes duplicates using SHA256 hashes,
and builds the document inventory.

Author: DECIMER Pipeline
"""

from pathlib import Path
from typing import List

import pandas as pd

from core.config import DOCUMENT_DATABASE_COLUMNS
from core.hashing import HashManager


class PDFInventory:
    """
    Handles PDF discovery and inventory creation.
    """

    def __init__(self):
        self._seen_hashes = set()

    def collect_pdfs(self, inputs: List[str]) -> List[Path]:
        """
        Collect PDF files from a list of files and/or directories.

        Parameters
        ----------
        inputs : List[str]

        Returns
        -------
        List[Path]
        """

        pdf_files = []

        for item in inputs:

            path = Path(item)

            if path.is_file() and path.suffix.lower() == ".pdf":
                pdf_files.append(path)

            elif path.is_dir():
                pdf_files.extend(sorted(path.rglob("*.pdf")))

        return pdf_files

    def build_inventory(self, pdf_paths: List[Path]) -> pd.DataFrame:
        """
        Build the document inventory.

        Duplicate PDFs are removed using SHA256 hashes.

        Parameters
        ----------
        pdf_paths : List[Path]

        Returns
        -------
        pd.DataFrame
        """

        records = []

        self._seen_hashes.clear()

        for pdf in pdf_paths:

            pdf_hash = HashManager.sha256(pdf)

            if pdf_hash in self._seen_hashes:
                continue

            self._seen_hashes.add(pdf_hash)

            records.append({

                "doc_id": None,

                "pdf_name": pdf.name,

                "pdf_hash": pdf_hash,

                "processed_on": None

            })

        return pd.DataFrame(records, columns=DOCUMENT_DATABASE_COLUMNS)

    def unique_pdfs(self, inventory: pd.DataFrame) -> List[str]:
        """
        Return the unique PDF names contained in the inventory.
        """

        return inventory["pdf_name"].tolist()