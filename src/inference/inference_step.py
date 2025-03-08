import logging
from controllers.game_strategy_controller import GameStrategyController
from utilities.image import ImageWrapper

class InferenceStep:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.next_step = None

    def set_next(self, next_step):
        """Sets the next inference step in the sequence."""
        self.next_step = next_step
        return next_step  # Allow chaining

    async def execute(self, image: ImageWrapper, game: GameStrategyController):
        """Executes the inference step and passes results to the next step if available."""
        await self.infer(image, game)
        if self.next_step:
            await self.next_step.execute(image, game)

    async def infer(self, image: ImageWrapper, game: GameStrategyController):
        """To be implemented by each inference type."""
        raise NotImplementedError("Subclasses must implement `infer` method")
