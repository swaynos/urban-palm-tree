# test_inference_step.py
import unittest
from unittest.mock import AsyncMock, MagicMock
from inference.inference_step import InferenceStep
from utilities.image import ImageWrapper
from controllers.game_flow_controller import GameFlowController

class TestInferenceStep(InferenceStep):
    async def infer(self, image: ImageWrapper, game: GameFlowController):
        return "inference_result"

class TestInferenceStepUnitTests(unittest.TestCase):
    def setUp(self):
        self.step = InferenceStep()
        self.test_step = TestInferenceStep()
        self.image_mock = MagicMock(spec=ImageWrapper)
        self.game_mock = MagicMock(spec=GameFlowController)

    def test_set_next(self):
        """Test that set_next correctly sets the next inference step."""
        self.step.set_next(self.test_step)
        self.assertEqual(self.step.next_step, self.test_step)

    async def test_execute_without_next_step(self):
        """Test execute method when there is no next step."""
        result = await self.step.execute(self.image_mock, self.game_mock)
        self.assertIsNone(result)

    async def test_execute_with_next_step(self):
        """Test execute method when there is a next step."""
        self.step.set_next(self.test_step)
        result = await self.step.execute(self.image_mock, self.game_mock)
        self.assertEqual(result, "inference_result")

    async def test_infer_not_implemented(self):
        """Test that the infer method raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            await self.step.infer(self.image_mock, self.game_mock)

if __name__ == '__main__':
    unittest.main()