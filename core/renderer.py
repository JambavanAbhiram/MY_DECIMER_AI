"""
core/renderer.py

Renders PDF pages into high-resolution PNG images.

Responsibilities
----------------
- Open PDF documents
- Render pages at configurable DPI
- Save rendered images
- Return metadata for each rendered page

Author: DECIMER Pipeline
"""

from pathlib import Path
from typing import List

import fitz
from PIL import Image


class PDFRenderer:
    """
    Renders PDF pages into PNG images.
    """

    def __init__(self, output_folder: Path, dpi: int = 300):
        self.output_folder = output_folder
        self.dpi = dpi

    def render_page(self, page: fitz.Page) -> Image.Image:
        """
        Render a single PDF page.

        Parameters
        ----------
        page : fitz.Page

        Returns
        -------
        PIL.Image
        """

        zoom = self.dpi / 72

        matrix = fitz.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        return image

    def render_pdf(self, pdf_path: Path) -> List[dict]:
        """
        Render every page of a PDF.

        Parameters
        ----------
        pdf_path : Path

        Returns
        -------
        List[dict]
            Metadata for every rendered page.
        """

        pdf_name = pdf_path.stem

        save_folder = self.output_folder / pdf_name

        save_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        document = fitz.open(pdf_path)

        page_records = []

        try:

            for page_index in range(len(document)):

                page = document.load_page(page_index)

                image = self.render_page(page)

                filename = (
                    f"{pdf_name}_page_{page_index + 1:03d}.png"
                )

                filepath = save_folder / filename

                image.save(filepath)

                page_records.append({

                    "pdf_name": pdf_name,

                    "page_number": page_index + 1,

                    "filename": filename,

                    "filepath": str(filepath),

                    "width": image.width,

                    "height": image.height,

                    "dpi": self.dpi

                })

        finally:

            document.close()

        return page_records