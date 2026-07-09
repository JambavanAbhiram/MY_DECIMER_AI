from pathlib import Path
from ultralytics import YOLO


class ChemicalStructureDetector:
    """
    Loads a trained YOLO model and performs chemical structure detection.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            project_root = Path(__file__).resolve().parent.parent
            model_path = project_root / "models" / "yolo" / "best.pt"

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found:\n{model_path}\n"
                "Place your trained 'best.pt' inside models/yolo/"
            )

        self.model = YOLO(str(model_path))

    def predict(self, image_path, **kwargs):
        """
        Run inference on an image.

        Parameters
        ----------
        image_path : str or Path
            Path to the image.

        Returns
        -------
        ultralytics.engine.results.Results
            Detection results.
        """
        return self.model.predict(
            source=str(image_path),
            verbose=False,
            **kwargs
        )

    def detect(self, image_path, **kwargs):
        """
        Alias for predict().
        """
        return self.predict(image_path, **kwargs)