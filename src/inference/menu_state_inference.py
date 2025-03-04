import logging
from controllers.game_flow_controller import GameFlowController
from game_state.menu_state import MenuState, get_menu_states
from inference.image_classification_inference import ImageClassifier
from inference.inference_step import InferenceStep
from utilities import config
from utilities.image import ImageWrapper

class MenuStateInference(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameFlowController):
        logger = logging.getLogger(__name__)
        menu_states_classes = get_menu_states()
        menu_status_image_classifier = ImageClassifier(
            config.HF_MENU_CLASSIFICATION_PATH, 
            config.IN_MENU_CLASSIFICATION_FILENAME, 
            menu_states_classes
        )
        menu_status_response, predictions = await menu_status_image_classifier.classify_image(image)

        if menu_status_response in [
            MenuState.SQUAD_BATTLES_OPPONENT_SELECTION,
            MenuState.FULL_TIME_MENU,
            MenuState.HALF_TIME_MENU,
        ] and predictions.max() > 0.5:
            return menu_status_response
        else:
            return MenuState.UNKNOWN
