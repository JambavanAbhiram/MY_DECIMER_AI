"""
pipeline.py

Main orchestration pipeline for the DECIMER project.

Responsibilities:
    • Accept PDF path or PDF blob
    • Generate document ID
    • Create output folder structure
    • Render PDF pages
    • Detect and crop chemical structures
    • Clean cropped images
    • Run DECIMER
    • Export metadata CSV

Author: Abhiram
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from core.config import OUTPUT_DIR, DELETE_TEMP_FILES
from core.hashing import generate_document_id
from core.inventory import InventoryManager
from core.renderer import PDFRenderer
from core.segmentation import StructureSegmenter
from recognition.processor import ImageProcessor
from core.metadata import MetadataManager


class Pipeline:

    def __init__(self):

        self.inventory = InventoryManager()
        self.renderer = PDFRenderer()
        self.segmenter = StructureSegmenter()
        self.processor = ImageProcessor()
        self.metadata = MetadataManager()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def run(self, input_data):
        """
        Process a PDF.

        Parameters
        ----------
        input_data : str | Path | bytes

        Returns
        -------
        dict
        """

        pdf_path = self._prepare_input(input_data)

        document_id = generate_document_id(pdf_path)

        # -------------------------------------------------
        # Create output folders
        # -------------------------------------------------

        document_dir = Path(OUTPUT_DIR) / document_id
        document_dir.mkdir(parents=True, exist_ok=True)

        metadata_csv = document_dir / "metadata.csv"

        try:

            # -------------------------------------------------
            # Register document
            # -------------------------------------------------

            self.inventory.register_document(
                document_id=document_id,
                pdf_path=pdf_path,
            )

            # -------------------------------------------------
            # Render pages
            # -------------------------------------------------

            rendered_pages = self.renderer.render(
                pdf_path=pdf_path,
                output_directory=document_dir,
            )

            # -------------------------------------------------
            # Process every rendered page
            # -------------------------------------------------

            for page in rendered_pages:

                page_directory = (
                    document_dir /
                    f"page_{page.page_number:03d}"
                )

                page_directory.mkdir(
                    parents=True,
                    exist_ok=True
                )

                detections = self.segmenter.segment(
                    page_image=page.image_path,
                    output_directory=page_directory,
                )

                for detection in detections:

                    cleaned = self.processor.process(
                        detection.image_path,
                        page_directory,
                    )

                    smiles = self.processor.run_decimer(
                        cleaned
                    )

                    self.metadata.add_entry(

                        document_id=document_id,

                        pdf_name=pdf_path.name,

                        page_number=page.page_number,

                        image_id=detection.image_id,

                        image_path=detection.image_path,

                        clean_image_path=cleaned,

                        image_type=detection.image_type,

                        is_formula=detection.is_formula,

                        smiles=smiles,

                        processing_status="SUCCESS",

                        error_message=""

                    )

            self.metadata.export(metadata_csv)

            return {

                "status": "SUCCESS",

                "document_id": document_id,

                "output_directory": str(document_dir),

                "metadata_csv": str(metadata_csv)

            }

        except Exception as e:

            self.metadata.add_pipeline_error(
                document_id=document_id,
                error_message=str(e)
            )

            self.metadata.export(metadata_csv)

            return {

                "status": "FAILED",

                "document_id": document_id,

                "error": str(e),

                "output_directory": str(document_dir)

            }

        finally:

            if DELETE_TEMP_FILES:
                self._cleanup_temp(pdf_path, input_data)

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _prepare_input(self, input_data):
        """
        Accept either

        • str
        • Path
        • bytes

        Returns a Path object.
        """

        if isinstance(input_data, (str, Path)):
            return Path(input_data)

        elif isinstance(input_data, bytes):

            temp_pdf = NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            )

            temp_pdf.write(input_data)
            temp_pdf.close()

            return Path(temp_pdf.name)

        raise TypeError(
            "Input must be a PDF path or PDF blob."
        )

    def _cleanup_temp(self, pdf_path, original_input):

        if isinstance(original_input, bytes):

            try:
                pdf_path.unlink(missing_ok=True)
            except Exception:
                pass