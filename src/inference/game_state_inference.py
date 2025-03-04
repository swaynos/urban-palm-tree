import logging
from controllers.game_flow_controller import GameFlowController
from game_state.game_state import GameState, get_game_states
from game_state.game_system_state import GameSystemState
from inference.image_classification_inference import ImageClassifier
from inference.inference_step import InferenceStep
from utilities import config
from utilities.image import ImageWrapper

class GameStateInference(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameFlowController):
        logger = logging.getLogger(__name__)
        menu_vs_match_classes = get_game_states()
        game_status_image_classifier = ImageClassifier(
            config.HF_MENU_VS_MATCH_PATH, 
            config.MENU_VS_MATCH_FILENAME, 
            menu_vs_match_classes
        )
        game_status_response, _ = await game_status_image_classifier.classify_image(image)

        if game_status_response == GameState.IN_MATCH:
            return GameSystemState.IN_MATCH_OTHER
        elif game_status_response == GameState.IN_MENU:
            return GameSystemState.IN_MENU_OTHER
        else:
            logger.warning(f"Unknown game state detected: {game_status_response}")
            return GameSystemState.UNKNOWN
