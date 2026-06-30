"""
core/segmentation.py

Chemical structure segmentation using DECIMER Segmentation.

Responsibilities
----------------
- Load rendered page images
- Segment chemical structures
- Save cropped structures
- Return metadata for each detected structure

Author: DECIMER Pipeline
"""

from pathlib import Path
from typing import List

import cv2
from PIL import Image

from decimer_segmentation import segment_chemical_structures


class ChemicalSegmenter:
    """
    Performs chemical structure segmentation on rendered pages.
    """

    def __init__(self, output_folder: Path):

        self.output_folder = output_folder

    def segment_page(self, page_record: dict) -> List[dict]:
        """
        Segment all chemical structures from a rendered page.

        Parameters
        ----------
        page_record : dict

        Returns
        -------
        List[dict]
        """

        page_path = Path(page_record["filepath"])

        pdf_name = page_record["pdf_name"]

        page_number = page_record["page_number"]

        page_stem = Path(page_record["filename"]).stem

        save_folder = self.output_folder / pdf_name

        save_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        image = cv2.imread(str(page_path))

        if image is None:
            return []

        structures = segment_chemical_structures(image)

        records = []

        for idx, structure in enumerate(structures):

            filename = (
                f"{page_stem}_structure_{idx + 1:03d}.png"
            )

            save_path = save_folder / filename

            Image.fromarray(structure).save(save_path)

            records.append({

                "pdf_name": pdf_name,

                "page_number": page_number,

                "structure_id": idx + 1,

                "image_path": str(save_path),

                "width": structure.shape[1],

                "height": structure.shape[0],

                "is_formula": None,

                "smiles": None,

                "processed": False

            })

        return records