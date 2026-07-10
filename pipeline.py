"""
pipeline.py

Main orchestration pipeline for the DECIMER project.
Updated for DECIMER Segmentation (no YOLO).
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from core.config import (
    OUTPUT_ROOT,
    DELETE_TEMP_FILES,
)

from core.hashing import generate_document_id
from core.inventory import InventoryManager
from core.renderer import PDFRenderer
from core.segmentation import StructureSegmenter
from core.metadata import MetadataManager

from recognition.cleaner import ImageCleaner
from recognition.processor import ImageProcessor


class Pipeline:

    def __init__(self):

        self.inventory = InventoryManager()
        self.renderer = PDFRenderer()
        self.segmenter = StructureSegmenter()
        self.cleaner = ImageCleaner()
        self.processor = ImageProcessor()
        self.metadata = MetadataManager()

    # ------------------------------------------------------------------

    def run(self, input_data):

        pdf_path = self._prepare_input(input_data)

        document_id = generate_document_id(pdf_path)

        document_dir = Path(OUTPUT_ROOT) / document_id
        document_dir.mkdir(parents=True, exist_ok=True)

        metadata_csv = document_dir / "metadata.csv"

        try:

            self.inventory.register_document(
                document_id=document_id,
                pdf_path=pdf_path,
            )

            rendered_pages = self.renderer.render(
                pdf_path=pdf_path,
                output_directory=document_dir,
            )

            for page in rendered_pages:

                page_directory = (
                    document_dir /
                    f"page_{page.page_number:03d}"
                )

                page_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                crop_directory = page_directory / "crops"
                clean_directory = page_directory / "cleaned"
                redraw_png_directory = page_directory / "redraw_png"
                redraw_svg_directory = page_directory / "redraw_svg"

                crop_directory.mkdir(exist_ok=True)
                clean_directory.mkdir(exist_ok=True)
                redraw_png_directory.mkdir(exist_ok=True)
                redraw_svg_directory.mkdir(exist_ok=True)

                crop_paths = self.segmenter.segment(
                    image_path=page.image_path,
                    output_dir=crop_directory,
                )

                for image_index, crop_path in enumerate(crop_paths, start=1):

                    crop_path = Path(crop_path)

                    cleaned_path = clean_directory / crop_path.name

                    self.cleaner.process(
                        crop_path,
                        cleaned_path,
                    )

                    redraw_png = (
                        redraw_png_directory /
                        f"{crop_path.stem}.png"
                    )

                    redraw_svg = (
                        redraw_svg_directory /
                        f"{crop_path.stem}.svg"
                    )

                    result = self.processor.process_image(
                        image_path=cleaned_path,
                        cleaned_path=cleaned_path,
                        redraw_png=redraw_png,
                        redraw_svg=redraw_svg,
                    )

                    self.metadata.add_entry(
                        document_id=document_id,
                        pdf_name=pdf_path.name,
                        page_number=page.page_number,
                        image_id=f"{page.page_number}_{image_index}",
                        image_path=str(crop_path),
                        clean_image_path=str(cleaned_path),
                        image_type="chemical_structure",
                        is_formula=True,
                        smiles=result.get("smiles"),
                        processing_status="SUCCESS" if result.get("success") else "FAILED",
                        error_message="" if result.get("success") else result.get("reason", ""),
                    )

            self.inventory.update_status(
                document_id,
                "SUCCESS",
            )

            self.metadata.export(metadata_csv)

            return {
                "status": "SUCCESS",
                "document_id": document_id,
                "output_directory": str(document_dir),
                "metadata_csv": str(metadata_csv),
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.inventory.update_status(
                document_id,
                "FAILED",
            )

            self.metadata.add_pipeline_error(
            document_id=document_id,
            error_message=str(e),
            )
            self.metadata.export(metadata_csv)

            return {
                "status": "FAILED",
                "document_id": document_id,
                "error": str(e),
                "output_directory": str(document_dir),
            }

        finally:

            if DELETE_TEMP_FILES:
                self._cleanup_temp(
                    pdf_path,
                    input_data,
                )

    # ------------------------------------------------------------------

    def _prepare_input(self, input_data):

        if isinstance(input_data, (str, Path)):
            return Path(input_data)

        if isinstance(input_data, bytes):

            temp_pdf = NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            )

            temp_pdf.write(input_data)
            temp_pdf.close()

            return Path(temp_pdf.name)

        raise TypeError(
            "Input must be a PDF path or PDF blob."
        )

    # ------------------------------------------------------------------

    def _cleanup_temp(
        self,
        pdf_path,
        original_input,
    ):

        if isinstance(original_input, bytes):

            try:
                Path(pdf_path).unlink(
                    missing_ok=True,
                )
            except Exception:
                pass
