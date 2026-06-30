"""
core/metadata.py

Metadata manager for the DECIMER Project.

Responsibilities
----------------
- Manage document_database.csv
- Manage master_database.csv
- Add/update documents
- Add/update images
- Prevent duplicates
- Provide lookup utilities

Author: DECIMER Project
"""

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from core.config import (
    DOCUMENT_DATABASE,
    MASTER_DATABASE,
    DOCUMENT_DATABASE_COLUMNS,
    MASTER_DATABASE_COLUMNS,
)


class MetadataManager:
    """
    Handles all metadata operations.
    """

    def __init__(self):

        self.document_database = DOCUMENT_DATABASE

        self.master_database = MASTER_DATABASE

        self._initialize()

    # ---------------------------------------------------------

    def _initialize(self):

        self.document_database.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.document_database.exists():

            pd.DataFrame(
                columns=DOCUMENT_DATABASE_COLUMNS
            ).to_csv(
                self.document_database,
                index=False,
            )

        if not self.master_database.exists():

            pd.DataFrame(
                columns=MASTER_DATABASE_COLUMNS
            ).to_csv(
                self.master_database,
                index=False,
            )

    # ---------------------------------------------------------

    def load_document_database(self):

        return pd.read_csv(
            self.document_database
        )

    # ---------------------------------------------------------

    def load_master_database(self):

        return pd.read_csv(
            self.master_database
        )

    # ---------------------------------------------------------

    def save_document_database(
        self,
        dataframe,
    ):

        dataframe.to_csv(
            self.document_database,
            index=False,
        )

    # ---------------------------------------------------------

    def save_master_database(
        self,
        dataframe,
    ):

        dataframe.to_csv(
            self.master_database,
            index=False,
        )

    # ---------------------------------------------------------

    def document_exists(
        self,
        pdf_hash: str,
    ) -> bool:

        df = self.load_document_database()

        return pdf_hash in df["pdf_hash"].values

    # ---------------------------------------------------------

    def image_exists(
        self,
        image_id: str,
    ) -> bool:

        df = self.load_master_database()

        return image_id in df["image_id"].values

    # ---------------------------------------------------------

    def add_document(
        self,
        record: Dict,
    ):

        df = self.load_document_database()

        df.loc[len(df)] = record

        self.save_document_database(df)

    # ---------------------------------------------------------

    def add_image(
        self,
        record: Dict,
    ):

        df = self.load_master_database()

        df.loc[len(df)] = record

        self.save_master_database(df)

    # ---------------------------------------------------------

    def update_image(
        self,
        image_id: str,
        **kwargs,
    ):

        df = self.load_master_database()

        index = df.index[
            df["image_id"] == image_id
        ]

        if len(index) == 0:

            return False

        index = index[0]

        for key, value in kwargs.items():

            if key in df.columns:

                df.at[index, key] = value

        self.save_master_database(df)

        return True

    # ---------------------------------------------------------

    def get_image(
        self,
        image_id: str,
    ) -> Optional[Dict]:

        df = self.load_master_database()

        row = df[
            df["image_id"] == image_id
        ]

        if row.empty:

            return None

        return row.iloc[0].to_dict()

    # ---------------------------------------------------------

    def get_document(
        self,
        doc_id: str,
    ) -> Optional[Dict]:

        df = self.load_document_database()

        row = df[
            df["doc_id"] == doc_id
        ]

        if row.empty:

            return None

        return row.iloc[0].to_dict()

    # ---------------------------------------------------------

    def mark_processed(
        self,
        image_id: str,
        smiles: str,
        clean_path: str,
        redraw_png: str,
        redraw_svg: str,
        confidence: float,
        agreement: float,
        votes: int,
        pubchem: bool,
        needs_review: bool,
        formula: str,
        molecular_weight: float,
        processed: str = "RECOGNIZED",
    ):

        self.update_image(

            image_id,

            smiles=smiles,

            clean_path=clean_path,

            redraw_png=redraw_png,

            redraw_svg=redraw_svg,

            confidence=confidence,

            agreement=agreement,

            votes=votes,

            pubchem=pubchem,

            needs_review=needs_review,

            formula=formula,

            molecular_weight=molecular_weight,

            processed=processed,

        )

    # ---------------------------------------------------------

    def failed(
        self,
        image_id: str,
        reason: str = "FAILED",
    ):

        self.update_image(

            image_id,

            processed=reason,

        )

    # ---------------------------------------------------------

    def statistics(self):

        df = self.load_master_database()

        return {

            "total_images": len(df),

            "recognized": int(
                (df["processed"] == "RECOGNIZED").sum()
            ),

            "failed": int(
                (df["processed"] == "FAILED").sum()
            ),

            "needs_review": int(
                df["needs_review"].fillna(False).sum()
            ),

        }

    # ---------------------------------------------------------

    def export(
        self,
        path: str | Path,
    ):

        df = self.load_master_database()

        df.to_csv(
            path,
            index=False,
        )