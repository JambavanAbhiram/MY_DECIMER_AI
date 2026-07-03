"""
inventory.py

Maintains a document-level inventory for all processed PDFs.

Responsibilities
----------------
1. Register new PDF documents
2. Check if a document was already processed
3. Store document-level metadata
4. Export inventory to CSV
"""

from pathlib import Path
from datetime import datetime
import pandas as pd

from core.config import OUTPUT_ROOT


class InventoryManager:

    INVENTORY_FILE = OUTPUT_ROOT / "document_inventory.csv"

    COLUMNS = [
        "document_id",
        "pdf_name",
        "pdf_path",
        "processed_on",
        "status"
    ]

    def __init__(self):

        if self.INVENTORY_FILE.exists():

            self.df = pd.read_csv(self.INVENTORY_FILE)

        else:

            self.df = pd.DataFrame(columns=self.COLUMNS)

            self.save()

    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------

    def register_document(
        self,
        document_id,
        pdf_path,
        status="PROCESSING"
    ):
        """
        Register a document in the inventory.
        """

        pdf_path = Path(pdf_path)

        if self.document_exists(document_id):
            return

        row = {

            "document_id": document_id,

            "pdf_name": pdf_path.name,

            "pdf_path": str(pdf_path.resolve()),

            "processed_on": datetime.now().isoformat(),

            "status": status

        }

        self.df.loc[len(self.df)] = row

        self.save()

    def update_status(
        self,
        document_id,
        status
    ):
        """
        Update processing status.
        """

        index = self.df[
            self.df["document_id"] == document_id
        ].index

        if len(index) == 0:
            return

        self.df.loc[index, "status"] = status

        self.save()

    def document_exists(
        self,
        document_id
    ):
        """
        Returns True if document already exists.
        """

        return document_id in self.df["document_id"].values

    def get_document(
        self,
        document_id
    ):
        """
        Return document information.
        """

        result = self.df[
            self.df["document_id"] == document_id
        ]

        if len(result) == 0:
            return None

        return result.iloc[0].to_dict()

    def list_documents(self):
        """
        Return entire inventory.
        """

        return self.df.copy()

    def save(self):
        """
        Save inventory CSV.
        """

        self.df.to_csv(
            self.INVENTORY_FILE,
            index=False
        )