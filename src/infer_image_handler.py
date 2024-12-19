import asyncio
import logging
import config
import monitoring

from game_state.game_state import GameState, get_game_states
from game_state.menu_state import MenuState, get_menu_states
from game_state.game_system_state import GameSystemState, get_game_system_states
from image import ImageWrapper
from image_classification_inference import ImageClassifier
from PIL import Image as PILImage
from yolo_object_detector import YoloObjectDetector
from shared_resources import exit_event

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler():
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
    from shared_resources import latest_screenshot
    
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
                await start_image_inference(image, logger)

            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)

async def start_image_inference(image: ImageWrapper, logger: logging.Logger):
    game_system_state = await infer_game_system_state(image)

    if game_system_state == GameSystemState.UNKNOWN:
        logger.debug("An unknown game system state has been detected")
    elif game_system_state == GameSystemState.IN_MENU_SQUAD_BATTLES_OPPONENT_SELECTION:
        squad_battles_opponent_selection_state = await infer_squad_selection_menu_state(image)
        # TODO: Implement game_actions based on the inferred state
    else:
        logger.debug(f"The game system state is {game_system_state}")

async def infer_game_system_state(image: ImageWrapper):
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

        # If the classifications aren't strong (all less than 50%), then ignore them
        if menu_status_response in menu_state_mapping and menu_status_predictions.max() > 0.5:
            return menu_state_mapping[menu_status_response]
        else:
            return GameSystemState.UNKNOWN
    else:
        raise ValueError(f"Unknown game state: {game_status_response}")
   

async def infer_squad_selection_menu_state(image_wrapper: ImageWrapper):
    """
    Infer the state of the squad selection menu by detecting objects near predefined points.

    Args:
        image_wrapper (ImageWrapper): An image wrapper containing the input image.

    Returns:
        dict: Mapping of points (A-F) to detected bounding boxes or None if no box contains the point.
    """
    # Setup
    # Define the cropping box for squad battles selection
    # (left, upper, right, lower)
    SQUAD_BATTLES_SELECTION_BBOX = (140, 363, 430, 908) 
    squad_selection_image_detection = YoloObjectDetector(config.HF_SQUAD_SELECTION_PATH, config.SQUAD_SELECTION_FILENAME)
    image = image_wrapper._image
    # Step 1: Validate image dimensions
    if image.size == (1280, 720):
        # Resize the image to 2560x1440
        image = image.resize((2560, 1440), PILImage.Resampling.LANCZOS)
    elif image.size != (2560, 1440):
        raise ValueError("Input image dimensions are expected to be 2560x1440.")

    # Step 2: Crop the image to the squad battles selection region
    cropped_image = image.crop(SQUAD_BATTLES_SELECTION_BBOX)

    # Step 3: Initialize the YOLO model and run predictions
    detector = YoloObjectDetector(config.HF_SQUAD_SELECTION_PATH, config.SQUAD_SELECTION_FILENAME)
    detections = await detector.detect_objects(cropped_image) 

    # TODO: Complete the method
    # 2. Crop the image to the desired region
    # 3. Run the YOLO model against the desired region
    
    raise NotImplementedError("Infer squad selection menu state")