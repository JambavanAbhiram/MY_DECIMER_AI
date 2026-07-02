"""
metadata.py

Metadata Manager

Responsibilities
----------------
1. Store image-level metadata.
2. Record pipeline errors.
3. Export metadata to CSV.

Author: Abhiram
"""

from pathlib import Path
import pandas as pd

from config import METADATA_COLUMNS


class MetadataManager:
    """
    Manages metadata for every detected chemical structure.
    """

    def __init__(self):
        self.records = []

    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------

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
        error_message=""
    ):
        """
        Add one processed image to the metadata.
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

            "error_message": error_message

        })

    # ---------------------------------------------------------

    def add_pipeline_error(
        self,
        document_id,
        error_message
    ):
        """
        Record a pipeline-level failure.
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

            "error_message": error_message

        })

    # ---------------------------------------------------------

    def export(
        self,
        csv_path
    ):
        """
        Export metadata to CSV.
        """

        csv_path = Path(csv_path)

        csv_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df = pd.DataFrame(
            self.records,
            columns=METADATA_COLUMNS
        )

        df.to_csv(
            csv_path,
            index=False
        )

    # ---------------------------------------------------------

    def clear(self):
        """
        Remove all stored metadata.
        """

        self.records.clear()

    # ---------------------------------------------------------

    def get_dataframe(self):
        """
        Return metadata as a pandas DataFrame.
        """

        return pd.DataFrame(
            self.records,
            columns=METADATA_COLUMNS
        )

    # ---------------------------------------------------------

    def __len__(self):
        """
        Number of metadata records.
        """

        return len(self.records)