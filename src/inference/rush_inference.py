from controllers.game_flow_controller import GameFlowController
from game_state.game_state import GameState
from inference.inference_step import InferenceStep
from inference.yolo_object_detector import YoloObjectDetector
from utilities import config
from utilities.image import ImageWrapper

def parse_rush_model_results(results):
    high_confidence = 0.35

    # Prepare detection results
    detections = []
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Extract coordinates
        confidence = result.conf[0].item()
        class_id = int(result.cls[0].item())
        class_name = results[0].names[class_id]

        detection = {
            "class_name": class_name, 
            "class_id": class_id,  # Class ID of detected object
            "points": {
                "x": x1,  # Convert to relative coordinates
                "y": y1,  # Convert to relative coordinates
                "width": (x2 - x1),
                "height": (y2 - y1)
            },
            "confidence": confidence
        }
        # Scrub the results. Only keep high confidence detections
        if class_name != "ball" and confidence > high_confidence:
            # Append detection to list
            detections.append(detection)
        # Unless it's the ball or the user controlled player
        elif class_name == "ball" or class_name == "user-controlled-player":
            detections.append(detection)
        
    return detections

class RushInference(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameFlowController):         
        yolo_detector = YoloObjectDetector(config.HF_RUSH_DETECTION_PATH, config.HF_RUSH_DETECTION_FILENAME)
        yolo_detection_results = await yolo_detector.detect_objects(image._image, parse_results_delegate=parse_rush_model_results)
        self.logger.debug(f"Rush inference detection results: {yolo_detection_results}")

        # If there are inference results, we are in a game. 
        # A successful run of this model should have lots of detections, decided to use 2 for now.
        if len(yolo_detection_results) > 2:
            game.game_state = GameState.IN_MATCH

            # Stop linked inference steps
            self.next_step = None
            
            