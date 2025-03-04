from controllers.game_flow_controller import GameFlowController
from utilities.image import ImageWrapper

class InferenceStep:
    def __init__(self):
        self.next_step = None

    def set_next(self, next_step):
        """Sets the next inference step in the sequence."""
        self.next_step = next_step
        return next_step  # Allow chaining

    async def execute(self, image: ImageWrapper, game: GameFlowController):
        """Executes the inference step and passes results to the next step if available."""
        result = await self.infer(image, game)
        if self.next_step:
            return await self.next_step.execute(image, game)
        return result

    async def infer(self, image: ImageWrapper, game: GameFlowController):
        """To be implemented by each inference type."""
        raise NotImplementedError("Subclasses must implement `infer` method")
