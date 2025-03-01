import aiofiles
import asyncio
import logging

from game_state.game_state import GameState, get_game_states
from game_state.game_system_state import GameSystemState
from game_state.menu_state import MenuState, get_menu_states
from game_state.squad_battles_tracker import SquadBattlesTracker
from game_strategy.generic_game_strategy import GenericGameStrategy
from game_strategy.in_match_strategy import InMatchStrategy
from game_strategy.squad_battles_selection_menu_strategy import SquadBattlesSelectionMenuStrategy
from inference.yolo_object_detector import YoloObjectDetector
import utilities.config as config
import utilities.monitoring as monitoring
from controllers.game_flow_controller import GameFlowController
from utilities.image import ImageWrapper
from inference.image_classification_inference import ImageClassifier
from utilities.shared_thread_resources import exit_event

infer_image_thread_statistics = monitoring.Statistics()

# TODO: Convert to class
async def infer_image_handler(game: GameFlowController):
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)

    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    # `latest_screenshot` holds the most recent screenshot to be processed for inference
    # TODO: Better manage dependency injection
    from utilities.shared_thread_resources import latest_screenshot
    
    while(not exit_event.is_set()):
        try:
            # Update statistics for monitoring purposes
            logger.debug(f"Has looped {infer_image_thread_statistics.count} times. Elapsed time is {infer_image_thread_statistics.get_time()}")
            infer_image_thread_statistics.count += 1

            image: ImageWrapper = None

            if (not latest_screenshot.empty()):
                image = await latest_screenshot.get()

            if(image is None):
                logger.warning("There is not a latest screenshot to infer from")
                await asyncio.sleep(1) # Sleep 1 second before trying again
            else:
                await start_image_inference(image, logger, game)

            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)

async def start_image_inference(image: ImageWrapper, logger: logging.Logger, game: GameFlowController):
    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    # `latest_actions_sequence` holds the most recent screenshot to be processed for inference
    # TODO: Better manage dependency injection
    from utilities.shared_thread_resources import latest_actions_sequence

    game_system_state = await infer_game_system_state(image, logger)

    if game_system_state == GameSystemState.UNKNOWN:
        logger.warning("An unknown game system state has been detected")
        
    elif game_system_state == GameSystemState.IN_MENU_SQUAD_BATTLES_OPPONENT_SELECTION:
        logger.info(f"The game system state is {game_system_state}, \
                     and will use the {SquadBattlesSelectionMenuStrategy.describe_strategy()}.") 
        squad_battles_opponent_selection_state = await infer_squad_selection_menu_state(image)
        strategy = SquadBattlesSelectionMenuStrategy(squad_battles_opponent_selection_state)
        actions = strategy.determine_action_from_state(image.get_timestamp(), game)
        await latest_actions_sequence.put(actions)

    elif game_system_state == GameSystemState.IN_MATCH_LIVE:
        strategy = InMatchStrategy(game_system_state)

        logger.info(f"The game system state is {game_system_state}, \
                     and will use the In Match Strategy.")
        
        actions = strategy.determine_action_from_state(image.get_timestamp(), game)
        await latest_actions_sequence.put(actions)
    else:
        strategy = GenericGameStrategy(game_system_state)

        logger.info(f"The game system state is {game_system_state}, \
                     and will use the Generic Game Strategy.")

        actions = strategy.determine_action_from_state(image.get_timestamp(), game)

        await latest_actions_sequence.put(actions)

async def infer_game_system_state(image: ImageWrapper, logger: logging.Logger):
    """
    Infers the game state from the provided image using classifiers to determine whether 
    the overall system state of the Game. Currently, this function uses two classifiers, but 
    ideally these will be merged into a single classifier to distinguish between
    defined GameSystemState. 

    Parameters:
    - self: Reference to the instance of the class where this method is defined.
    - image (ImageWrapper): The image object which will be analyzed for game state inference.
    """
    # Initialize the menu vs. match image classifier
    # TODO: Train a single classifier for GameSystemState
    menu_vs_match_classes = get_game_states()
    menu_states_classes = get_menu_states()
    game_status_image_classifier = ImageClassifier(config.HF_MENU_VS_MATCH_PATH, config.MENU_VS_MATCH_FILENAME, menu_vs_match_classes)
    menu_status_image_classifier = ImageClassifier(config.HF_MENU_CLASSIFICATION_PATH, config.IN_MENU_CLASSIFICATION_FILENAME, menu_states_classes)
    
    game_status_response, game_status_predictions = await game_status_image_classifier.classify_image(image)

    if game_status_response == GameState.IN_MATCH:
        return GameSystemState.IN_MATCH_OTHER
    elif game_status_response == GameState.IN_MENU:
        menu_state_mapping = {
            MenuState.SQUAD_BATTLES_OPPONENT_SELECTION: GameSystemState.IN_MENU_SQUAD_BATTLES_OPPONENT_SELECTION,
            MenuState.FULL_TIME_MENU: GameSystemState.IN_MATCH_MENU,
            MenuState.HALF_TIME_MENU: GameSystemState.IN_MATCH_MENU, 
            MenuState.MENU_POST_MATCH_SUMMARY: GameSystemState.IN_MATCH_POST_MATCH_SUMMARY,
            MenuState.UNKNOWN: GameSystemState.IN_MENU_OTHER
        }
        menu_status_response, menu_status_predictions = await menu_status_image_classifier.classify_image(image)

        # If the classifications aren't strong (all less than 50%), then we will ignore them
        if menu_status_response in menu_state_mapping and menu_status_predictions.max() > 0.5:
            return menu_state_mapping[menu_status_response]
        else:
            return GameSystemState.IN_MENU_OTHER
    else:
        logger.warning(f"Unknown game state: {game_status_response}")
        return GameSystemState.UNKNOWN

# TODO: Unit Test is_point_in_bbox()
# Function to check if a point is within a bounding box
def is_point_in_bbox(point, bbox):
    x, y = point
    left, upper, right, lower = bbox
    return left <= x <= right and upper <= y <= lower

   
# TODO: The squad selection methods can be moved into their own Class
async def infer_squad_selection_menu_state(image_wrapper: ImageWrapper):
    """
    Infer the state of the squad selection menu by detecting objects near predefined points.

    Args:
        image_wrapper (ImageWrapper): An image wrapper containing the input image.

    Returns:
        SquadBattlesTracker: the state of the squad battles menu from the object detection model.
    """
    # Setup
    # Define the cropping box for squad battles selection
    # (left, upper, right, lower)
    SQUAD_BATTLES_SELECTION_BBOX = (140, 363, 430, 908) 
    detector = YoloObjectDetector(config.HF_SQUAD_SELECTION_PATH, config.SQUAD_SELECTION_FILENAME)
    image = image_wrapper._image
    # Step 1: Validate image dimensions
    # We understand what to do if the dimensions are 720p
    if image.size == (1280, 720):
        image_wrapper.resize(2560, 1440)
    # If the dimension is not 1440p, then halt execution
    elif image.size != (2560, 1440):
        raise ValueError(f"Input image dimensions are expected to be 2560x1440. Received {image.width}x{image.height}.")

    # Step 2: Crop the image to the squad battles selection region
    cropped_image = image.crop(SQUAD_BATTLES_SELECTION_BBOX)

    # Step 3: Initialize the YOLO model and run predictions
    detections = await detector.detect_objects(cropped_image) 

    return evaluate_squad_selection_menu_state_detections(detector.model.names, detections)

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

