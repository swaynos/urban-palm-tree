import asyncio
import logging
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)

class YoloObjectDetector:
    """
    A wrapper class for running YOLO model inference to detect objects and bounding boxes.
    """

    def __init__(self, modelpath, filename, conf_threshold=0.25):
        """
        Initialize the YOLO object detector.

        Args:
            modelpath (str): Path to the model on HuggingFace Hub.
            filename (str): Model file name.
            conf_threshold (float): Confidence threshold for detections.
        """
        self.modelpath = hf_hub_download(modelpath, filename)
        self.model = YOLO(self.modelpath)
        self.conf_threshold = conf_threshold
        logger.info(f"YOLO model loaded from {self.modelpath}")

    async def detect_objects(self, image_wrapper):
        """
        Run the YOLO model to detect objects in the input image.

        Args:
            image_wrapper (ImageWrapper): An instance of ImageWrapper with a valid image.

        Returns:
            List[dict]: List of detections with class names, confidence scores, and bounding boxes.
        """
        logger.debug("Starting object detection on the provided image.")

        # Retrieve the PIL image directly from the ImageWrapper
        image = image_wrapper._image

        # Run prediction in an executor thread to make it async-compatible
        results = await asyncio.to_thread(
            self.model.predict,
            source=image,
            conf=self.conf_threshold
        )

        detections = self._parse_results(results)
        return detections

    def _parse_results(self, results):
        """
        Parse YOLO results into a user-friendly format.

        Args:
            results: The result object from YOLO prediction.

        Returns:
            List[dict]: A list of detections with class names, confidence scores, and bounding boxes.
        """
        parsed_detections = []
        for result in results:
            for box in result.boxes.data.tolist():
                x1, y1, x2, y2, confidence, class_id = box
                parsed_detections.append({
                    "class": result.names[int(class_id)],
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })
        logger.debug(f"Detections: {parsed_detections}")
        return parsed_detections