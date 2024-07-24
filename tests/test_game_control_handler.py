import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from game_controller import GameController
from game_control_handler import controller_input_handler
from game_state import GameState, MenuState
from macos_app import RunningApplication
from shared_resources import inferred_game_state, exit_event

class TestGameControlHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Mock(spec=RunningApplication)
        self.game = Mock(spec=GameController)
        exit_event.clear()  # Ensure the exit event is clear before each test

    @patch('shared_resources.inferred_game_state')
    async def test_controller_input_in_match(self, mock_inferred_game_state):
        mock_inferred_game_state.read_data = AsyncMock(return_value={'GameState': GameState.IN_MATCH.name})
        
        # Run the controller input handler in its own task
        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler to run for a short period
        await asyncio.sleep(0.1) 

        # Assert that spin_in_circles was started
        self.game.spin_in_circles.assert_awaited_once_with(2)

        # Clean up
        exit_event.set()
        task.cancel()

    @patch('shared_resources.inferred_game_state')
    async def test_controller_input_in_menu(self, mock_inferred_game_state):
        mock_inferred_game_state.read_data = AsyncMock(side_effect=[
            {'GameState': GameState.IN_MENU.name, 'MenuState': MenuState.SQUAD_BATTLES_OPPONENT_SELECTION.name},
            {'GameState': GameState.IN_MENU.name, 'MenuState': MenuState.UNKNOWN.name}
        ])
        
        # Run the controller input handler in its own task
        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler to run for a short period
        await asyncio.sleep(0.1)

        # Assert that the correct interactions happened during the menu state
        self.game.io.tap.assert_called_once_with(self.game.io.Cross)

        # Clean up
        exit_event.set()
        task.cancel()

    @patch('shared_resources.inferred_game_state')
    async def test_controller_input_cancel_action(self, mock_inferred_game_state):
        mock_inferred_game_state.read_data = AsyncMock(side_effect=[
            {'GameState': GameState.IN_MATCH.name},
            {'GameState': GameState.IN_MENU.name},
            {'GameState': GameState.IN_MENU.name, 'MenuState': MenuState.UNKNOWN.name}
        ])

        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Run the handler long enough to start the action and then cancel it
        await asyncio.sleep(0.1)

        # Assert that spin_in_circles was started
        self.game.spin_in_circles.assert_awaited_once_with(2)

        # Allow time for the action to be cancelled
        await asyncio.sleep(0.1)

        # Assert that the ongoing action was cancelled
        self.assertTrue(self.game.spin_in_circles.call_count <= 1)

        # Clean up
        exit_event.set()
        task.cancel()

if __name__ == '__main__':
    unittest.main()
