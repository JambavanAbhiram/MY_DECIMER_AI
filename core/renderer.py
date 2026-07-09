"""
renderer.py

PDF Rendering Module

Responsibilities
----------------
1. Render each page of a PDF to an image.
2. Save page images into the appropriate document/page folder.
3. Return information about the rendered pages.

Author: Abhiram
"""

from dataclasses import dataclass
from pathlib import Path
import fitz  # PyMuPDF

from core.config import (
    RENDER_DPI,
    IMAGE_FORMAT,
    PAGE_NAME_TEMPLATE,
    RAW_IMAGE_FOLDER,
)


@dataclass
class RenderedPage:
    """
    Represents one rendered PDF page.
    """

    page_number: int
    image_path: Path


class PDFRenderer:

    def __init__(self, dpi=RENDER_DPI):
        self.dpi = dpi

    def render(
        self,
        pdf_path: Path,
        output_directory: Path,
    ):
        """
        Render every page of the PDF.

        Parameters
        ----------
        pdf_path : Path
            Input PDF

        output_directory : Path
            Document output folder

        Returns
        -------
        list[RenderedPage]
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        document = fitz.open(pdf_path)

        rendered_pages = []

        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for page_index in range(len(document)):

            page = document.load_page(page_index)

            page_folder = (
                output_directory /
                PAGE_NAME_TEMPLATE.format(page_index + 1)
            )

            raw_folder = page_folder / RAW_IMAGE_FOLDER

            raw_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            image_path = (
                raw_folder /
                f"page.{IMAGE_FORMAT}"
            )

            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            pix.save(str(image_path))

            rendered_pages.append(

                RenderedPage(

                    page_number=page_index + 1,

                    image_path=image_path

                )

            )

        document.close()

        return rendered_pages