"""
metadata.py

Metadata Manager

Stores metadata for every chemical structure processed by the
DECIMER pipeline.
"""

from pathlib import Path
import pandas as pd

from core.config import METADATA_COLUMNS


class MetadataManager:
    """
    Stores metadata for every processed chemical structure.

    Records are accumulated in memory and exported to CSV
    at the end of pipeline execution.
    """

    def __init__(self):
        self.records = []

    # ------------------------------------------------------------------
    # Structure Metadata
    # ------------------------------------------------------------------

    def add_entry(
        self,
        document_id,
        pdf_name,
        page_number,
        image_id,
        image_path,
        clean_image_path,
        image_type,
        is_formula,
        smiles,
        processing_status,
        error_message="",
        confidence=None,
        agreement=None,
        votes=None,
        trust=None,
        pubchem=None,
        needs_review=None,
        formula=None,
        molecular_weight=None,
        engine=None,
        canonical_smiles=None,
        heavy_atoms=None,
        atom_count=None,
        valid=None,
    ):
        """
        Store metadata for one processed image.
        """

        self.records.append({

            "document_id": document_id,

            "pdf_name": pdf_name,

            "page_number": page_number,

            "image_id": image_id,

            "image_path": str(image_path),

            "clean_image_path": str(clean_image_path),

            "image_type": image_type,

            "is_formula": is_formula,

            "engine": engine,

            "smiles": smiles,

            "canonical_smiles": canonical_smiles,

            "formula": formula,

            "molecular_weight": molecular_weight,

            "heavy_atoms": heavy_atoms,

            "atom_count": atom_count,

            "confidence": confidence,

            "agreement": agreement,

            "votes": votes,

            "trust": trust,

            "pubchem": pubchem,

            "valid": valid,

            "needs_review": needs_review,

            "processing_status": processing_status,

            "error_message": error_message,

        })

    # ------------------------------------------------------------------
    # Pipeline Errors
    # ------------------------------------------------------------------

    def add_pipeline_error(
        self,
        document_id,
        error_message,
    ):
        """
        Store a pipeline-level failure.
        """

        self.records.append({

            "document_id": document_id,

            "pdf_name": "",

            "page_number": "",

            "image_id": "",

            "image_path": "",

            "clean_image_path": "",

            "image_type": "",

            "is_formula": "",

            "engine": None,

            "smiles": None,

            "canonical_smiles": None,

            "formula": None,

            "molecular_weight": None,

            "heavy_atoms": None,

            "atom_count": None,

            "confidence": None,

            "agreement": None,

            "votes": None,

            "trust": None,

            "pubchem": None,

            "valid": False,

            "needs_review": None,

            "processing_status": "FAILED",

            "error_message": error_message,

        })

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(
        self,
        csv_path,
    ):
        """
        Export metadata as CSV.
        """

        csv_path = Path(csv_path)

        csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df = pd.DataFrame(
            self.records,
            columns=METADATA_COLUMNS,
        )

        df.to_csv(
            csv_path,
            index=False,
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self):
        """Remove all stored metadata."""
        self.records.clear()

    # ------------------------------------------------------------------

    def get_dataframe(self):
        """Return metadata as a pandas DataFrame."""

        return pd.DataFrame(
            self.records,
            columns=METADATA_COLUMNS,
        )

    # ------------------------------------------------------------------

    def __len__(self):
        return len(self.records)

    # ------------------------------------------------------------------

    def __iter__(self):
        return iter(self.records)