import logging
from controllers.game_flow_controller import GameFlowController
from game_state.squad_battles_tracker import SquadBattlesTracker
from inference.inference_step import InferenceStep
from inference.yolo_object_detector import YoloObjectDetector
from utilities import config
from utilities.bbox import is_point_in_bbox
from utilities.image import ImageWrapper

class SquadSelectionInference(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameFlowController):
        logger = logging.getLogger(__name__)
        
        # Define the cropping box for squad battles selection
        # (left, upper, right, lower)
        SQUAD_BATTLES_SELECTION_BBOX = (140, 363, 430, 908) 

        detector = YoloObjectDetector(config.HF_SQUAD_SELECTION_PATH, config.SQUAD_SELECTION_FILENAME)
        
        # Step 1: Validate image dimensions
        _image = image._image # Unwrap the image
        # If the image is 720p, then resize it to 1440p
        if _image.size == (1280, 720):
            image.resize(2560, 1440)
        # If the dimension is not 1440p, then halt execution
        elif _image.size != (2560, 1440):
            raise ValueError(f"Input image dimensions are expected to be 2560x1440. Received {image.width}x{image.height}.")
        # TODO: This image processing can be improved to better support many different resolutions

        # Step 2: Crop the image to the squad battles selection region
        cropped_image = _image.crop(SQUAD_BATTLES_SELECTION_BBOX)

        # Step 3: Initialize the YOLO model and run predictions
        detections = await detector.detect_objects(cropped_image)

        return self.evaluate_squad_selection_menu_state_detections(detector.model.names, detections)
    
    # TODO: Unit Test evaluate_detections()
    def evaluate_squad_selection_menu_state_detections(class_names, detections) -> SquadBattlesTracker:
        # The squad selection menu can be thought of as the following:
        # [0] [1]
        # [2] [3]
        # [4] [5]
        # Where 0->5 could be arranged as a collection of tuples
        points = [(73, 130),
        (220, 130),
        (73, 330),
        (220, 330),
        (73, 470),
        (220, 470)]
        
        squad_battles_tracker = SquadBattlesTracker()

        # For each detection made evaluate the points A->F to see
        # if any fall within the bounding box.
        # Iterate through each detection made
        for detection in detections:
            detection_bbox = detection['bbox']  # Modify this as per your detection output structure

            # Check each point to see if it's within the detection bounding box
            for index, point in enumerate(points):
                if is_point_in_bbox(point, detection_bbox):
                    # Squad Selected
                    if (detection['class'] == class_names[1]):
                        if (index % 2 == 0):
                            squad_battles_tracker.current_col = 0
                        else:
                            squad_battles_tracker.current_col = 1
                        if (index < 2):
                            squad_battles_tracker.current_row = -1 # the current tracker wasn't built to support the top row
                        elif (index < 4):
                            squad_battles_tracker.current_row = 0
                        elif (index < 6):
                            squad_battles_tracker.current_row = 1
                        else:
                            squad_battles_tracker.current_row = -1 # if unknown, lets just assume the top row
                    
                    # Squad Played
                    elif (detection['class'] == class_names[0]):
                        if (index == 2):
                            squad_battles_tracker.grid[0][0] = True
                        elif (index == 3):
                            squad_battles_tracker.grid[0][1] = True
                        elif (index == 4):
                            squad_battles_tracker.grid[1][0] = True
                        elif (index == 5):
                            squad_battles_tracker.grid[1][1] = True

        return squad_battles_tracker
