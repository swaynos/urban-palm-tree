from controllers.game_strategy_controller import GameStrategyController
from game_state.game_state import GameState, get_game_states
from game_state.game_system_state import GameSystemState
from inference.image_classification_inference import ImageClassifier
from inference.inference_step import InferenceStep
from utilities import config
from utilities.image import ImageWrapper

class GameStateInference(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameStrategyController):
        menu_vs_match_classes = get_game_states()
        game_status_image_classifier = ImageClassifier(
            config.HF_MENU_VS_MATCH_PATH, 
            config.MENU_VS_MATCH_FILENAME, 
            menu_vs_match_classes
        )
        game_status_response, _ = await game_status_image_classifier.classify_image(image)

        game.game_state_tracker.set_game_state(game_status_response)

        # TODO: I think as it stands today, the different levels of state are too complicated to manage. Refactoring is suggested.
        
        # if game_status_response == GameState.IN_MATCH:
        #     game.game_state_tracker.set_game_state(GameSystemState.IN_MATCH_OTHER)
        # elif game_status_response == GameState.IN_MENU:
        #     game.game_state_tracker.update_data(GameSystemState.IN_MENU_OTHER)
        # else:
        #     self.logger.warning(f"Unknown game state detected: {game_status_response}")
        #     game.game_state_tracker.update_data(GameSystemState.UNKNOWN)

        # From here the pipeline can be modified based on the game state. See notes in Readme.md
