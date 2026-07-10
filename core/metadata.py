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

    def __init__(self):
        self.records = []

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
    ):
        """
        Add one processed chemical structure.
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

            "smiles": smiles,

            "processing_status": processing_status,

            "error_message": error_message,

            "confidence": confidence,

            "agreement": agreement,

            "votes": votes,

            "trust": trust,

            "pubchem": pubchem,

            "needs_review": needs_review,

            "formula": formula,

            "molecular_weight": molecular_weight,

        })

    # ------------------------------------------------------------------

    def add_pipeline_error(
        self,
        document_id,
        error_message,
    ):
        """
        Store a pipeline-level error.
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

            "smiles": "",

            "processing_status": "FAILED",

            "error_message": error_message,

            "confidence": None,

            "agreement": None,

            "votes": None,

            "trust": None,

            "pubchem": None,

            "needs_review": None,

            "formula": None,

            "molecular_weight": None,

        })

    # ------------------------------------------------------------------

    def export(
        self,
        csv_path,
    ):
        """
        Export metadata to CSV.
        """

        csv_path = Path(csv_path)

        csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df = pd.DataFrame(
            self.records
        )

        df.to_csv(
            csv_path,
            index=False,
        )

    # ------------------------------------------------------------------

    def clear(self):
        self.records.clear()

    # ------------------------------------------------------------------

    def get_dataframe(self):

        return pd.DataFrame(
            self.records
        )

    # ------------------------------------------------------------------

    def __len__(self):
        return len(self.records)