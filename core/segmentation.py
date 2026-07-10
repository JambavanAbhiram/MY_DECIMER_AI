"""
segmentation.py

Chemical structure segmentation using DECIMER Segmentation.

Input:
    Path to a rendered PDF page.

Output:
    List of cropped chemical structure image paths.
"""

from pathlib import Path
from typing import List

import cv2
from decimer_segmentation import segment_chemical_structures_from_file


class StructureSegmenter:
    """
    Wrapper around DECIMER Segmentation.

    Given a rendered PDF page, extracts all chemical structures
    and saves them as individual images.
    """

    def __init__(self):
        pass

    def segment(
        self,
        image_path: str,
        output_dir: str
    ) -> List[str]:
        """
        Segment chemical structures from a page image.

        Parameters
        ----------
        image_path : str
            Path to rendered page image.

        output_dir : str
            Directory where cropped structures will be saved.

        Returns
        -------
        List[str]
            Paths to cropped structure images.
        """

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = Path(image_path)

        structures = segment_chemical_structures_from_file(str(image_path), expand=True)

        saved_images = []

        stem = Path(image_path).stem

        for idx, structure in enumerate(structures):

            save_path = output_dir / f"{stem}_structure_{idx+1}.png"

            cv2.imwrite(str(save_path), structure)

            saved_images.append(str(save_path))

        return saved_images