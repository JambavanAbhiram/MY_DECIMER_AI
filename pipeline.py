"""
pipeline.py

Main orchestration pipeline for the DECIMER Project.

Supports

    • PDF files
    • Image files
    • Folders containing either

Pipeline

PDF
    ↓
Render
    ↓
Segment
    ↓
Recognition

PNG
    ↓
Recognition

Author: DECIMER Project
"""

from datetime import datetime
from pathlib import Path
import uuid

from core.config import (
    DEFAULT_DPI,
    RENDERED_FOLDER,
    SEGMENTED_FOLDER,
    CLEANED_FOLDER,
)

from core.inventory import PDFInventory
from core.metadata import MetadataManager
from core.renderer import PDFRenderer
from core.segmentation import ChemicalSegmenter
from core.hashing import HashManager

from recognition.processor import RecognitionProcessor


class Pipeline:

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
    }

    def __init__(self):

        self.inventory = PDFInventory()

        self.metadata = MetadataManager()

        self.renderer = PDFRenderer(
            output_folder=RENDERED_FOLDER,
            dpi=DEFAULT_DPI,
        )

        self.segmenter = ChemicalSegmenter(
            output_folder=SEGMENTED_FOLDER,
        )

        self.recognition = RecognitionProcessor()

    # ------------------------------------------------------------

    def run(self, inputs):

        for item in inputs:
            path = Path(item)

            if not path.exists():
                print(f"Skipping {path}")
                continue

            if path.is_file():
                self._process_file(path)

            elif path.is_dir():
                self._process_folder(path)
        print("\nPipeline finished.")

    # ------------------------------------------------------------

    def _process_folder(self, folder):

        for file in sorted(folder.rglob("*")):
            if file.is_file():
                self._process_file(file)

    # ------------------------------------------------------------

    def _process_file(self, file):

        suffix = file.suffix.lower()

        if suffix == ".pdf":
            self._process_pdf(file)

        elif suffix in self.IMAGE_EXTENSIONS:
            self._process_image(file)

    # ------------------------------------------------------------

    def _process_pdf(self, pdf_path):

        pdf_hash = HashManager.sha256(pdf_path)

        if self.metadata.document_exists(pdf_hash):
            print(f"Skipping duplicate PDF: {pdf_path.name}")
            return
        
        doc_id = str(uuid.uuid4())

        self.metadata.add_document({
            "doc_id": doc_id,
            "pdf_name": pdf_path.name,
            "pdf_hash": pdf_hash,
            "processed_on": datetime.now(),
        })

        print(f"\nProcessing PDF : {pdf_path.name}")
        pages = self.renderer.render_pdf(pdf_path)

        for page in pages:
            structures = self.segmenter.segment_page(page)

            for structure in structures:
                self._recognize_structure(
                    doc_id,
                    pdf_path.name,
                    structure,
                )

    # ------------------------------------------------------------

    def _process_image(self, image_path):

        print(f"\nProcessing Image : {image_path.name}")
        structure = {
            "page_number": 1,
            "image_path": str(image_path),
        }

        self._recognize_structure(
            None,
            image_path.name,
            structure,
        )

    # ------------------------------------------------------------

    def _recognize_structure(self, doc_id, document_name, structure):
        image_id = str(uuid.uuid4())
        image_path = Path(
            structure["image_path"]
        )

        cleaned = (
            CLEANED_FOLDER
            / f"{image_id}.png"
        )

        redraw_png = (
            CLEANED_FOLDER
            / f"{image_id}_redraw.png"
        )

        redraw_svg = (
            CLEANED_FOLDER
            / f"{image_id}_redraw.svg"
        )

        result = self.recognition.process_image(
            image_path,
            cleaned,
            redraw_png,
            redraw_svg,
        )

        self.metadata.add_image({
            "doc_id": doc_id,
            "pdf_name": document_name,
            "page_number": structure.get(
                "page_number",
                1,
            ),
            "image_id": image_id,
            "image_path": str(image_path),
            "clean_path": str(cleaned),
            "image_type": "FORMULA",
            "is_formula": result["success"],
            "smiles": result.get(
                "smiles",
                "",
            ),
        
            "processed": (
                "RECOGNIZED"
                if result["success"]
                else "FAILED"
            ),
        })

        if result["success"]:
            print(
                f"{image_path.name}"
                f" -> {result['smiles']}"
            )
        else:
            print(
                f"{image_path.name}"
            )