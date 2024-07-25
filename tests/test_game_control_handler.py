import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from game_controller import GameController
from game_control_handler import controller_input_handler
from game_state import GameState, MenuState
from macos_app import RunningApplication
from playstation_io import PlaystationIO
from shared_resources import exit_event

class TestGameControlHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Mock(spec=RunningApplication)
        self.game = Mock(spec=GameController)
        self.game.io = Mock(spec=PlaystationIO)

        # Define some mocks for inferred game state for different scenarios
        self.mock_in_match = {
            'GameState': GameState.IN_MATCH.name,
            'MenuState': None,
            'MatchState': None,
        }
        self.mock_in_menu = {
            'GameState': GameState.IN_MENU.name,
            'MenuState': MenuState.MENU_POST_MATCH_SUMMARY.name,
            'MatchState': None,
        }
        self.mock_in_menu_unknown = {
            'GameState': GameState.IN_MENU.name,
            'MenuState': MenuState.UNKNOWN.name,
            'MatchState': None,
        }
        self.mock_in_menu_squad_battles_opponent_selection= {
            'GameState': GameState.IN_MENU.name,
            'MenuState': MenuState.SQUAD_BATTLES_OPPONENT_SELECTION.name,
            'MatchState': None,
        }

        # Ensure the exit event is clear before each test
        exit_event.clear()  

    @patch('shared_resources.inferred_game_state')
    async def test_controller_input_in_match(self, mock_inferred_game_state):
        mock_inferred_game_state.read_data = AsyncMock(return_value=self.mock_in_match)
        
        # Run the controller input handler in its own task
        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler priority on the event loop for a very short time
        await asyncio.sleep(0.01) 

        # Assert that spin_in_circles was started
        self.assertGreater(self.game.spin_in_circles.call_count, 0)

        # Clean up
        exit_event.set()
        task.cancel()

    @patch('shared_resources.inferred_game_state')
    async def test_controller_input_in_menu(self, mock_inferred_game_state): 
        mock_inferred_game_state.read_data = AsyncMock(return_value=self.mock_in_menu)
        
        # Run the controller input handler in its own task
        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler priority on the event loop for a very short time
        await asyncio.sleep(0.01)

        # Assert that the correct interactions happened during the menu state
        self.assertGreater(self.game.io.tap.call_count, 0)

        # Clean up
        exit_event.set()
        task.cancel()

    @patch('shared_resources.inferred_game_state')
    @patch('game_control_handler.create_ongoing_action')
    async def test_controller_input_cancel_action(self, mock_create_ongoing_action, mock_inferred_game_state):
        mock_inferred_game_state.read_data = AsyncMock(return_value=self.mock_in_match)
    
        # Create a mock for the ongoing action/task
        mock_task = AsyncMock()
        mock_create_ongoing_action.return_value = mock_task  # Ensure it returns the mock task

        # Run the controller input handler in its own task
        handler_task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler to run for a short while
        await asyncio.sleep(0.01)

        # Assert that create_ongoing_action was called because it should have processed the match state
        self.assertEqual(mock_create_ongoing_action.call_count, 1)

        mock_inferred_game_state.read_data = AsyncMock(return_value=self.mock_in_menu_squad_battles_opponent_selection)

        # Clean up
        exit_event.set()  # Ensure you signal the handler to stop
        handler_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await handler_task  # This ensures that the task was cancelled correctly

if __name__ == '__main__':
    unittest.main()
