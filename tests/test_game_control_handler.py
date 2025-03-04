import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, call, patch

from controllers.game_flow_controller import GameFlowController
from handlers.game_control_handler import controller_input_handler
from game_state import GameState, MenuState
from utilities.macos_app import RunningApplication
from utilities.playstation_io import PlaystationIO
from utilities.shared_thread_resources import exit_event

class TestGameControlHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Mock(spec=RunningApplication)
        self.game = Mock(spec=GameFlowController)
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
         
    async def shared_cleanup(self, handler_task):
         # Common cleanup code
        exit_event.set()  # Ensure you signal the handler to stop
        handler_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await handler_task  # This ensures that the task was cancelled correctly

    @patch('utilities.shared_thread_resources.inferred_game_state')
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

    @patch('utilities.shared_thread_resources.inferred_game_state')
    async def test_controller_input_in_menu(self, mock_inferred_game_state): 
        mock_inferred_game_state.read_data = AsyncMock(return_value=self.mock_in_menu)
        
        # Run the controller input handler in its own task
        task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Allow the handler priority on the event loop for a very short time
        await asyncio.sleep(0.1)

        # Assert that the correct interactions happened during the menu state
        self.assertGreater(self.game.io.tap.call_count, 0)

        # Clean up
        exit_event.set()
        task.cancel()

    @patch('utilities.shared_thread_resources.inferred_game_state')
    @patch('game_control_handler.create_ongoing_action')
    async def test_controller_input_cancel_action(self, mock_create_ongoing_action, mock_inferred_game_state):
        # Define a generator function for your responses
        def mock_inferred_game_state_responses():
            for _ in range(10):  # First 10 calls return in_match
                yield self.mock_in_match
            while True:  # Subsequent calls return in_menu infinitely
                yield self.mock_in_menu

        # Create an AsyncMock instance for read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())
        
        # Assign `AsyncMock` to read_data
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Mock the create_ongoing_action function to return a mock task
        mock_create_ongoing_action.return_value = asyncio.create_task(asyncio.sleep(5))

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Yield control back to the handler to let it run once
        await asyncio.sleep(0)

        # Assert that create_ongoing_action was called because it should have processed the match state
        self.assertEqual(mock_create_ongoing_action.call_count, 1)

        # Allow a short wait for the transition to menu to take place
        await asyncio.sleep(0.01)

        # Ensure the mock ongoing task was canceled
        self.assertEqual(mock_create_ongoing_action.return_value._state, 'CANCELLED')  

        # Clean up
        self.shared_cleanup(handler_task)

    @patch('utilities.shared_thread_resources.inferred_game_state')
    @patch('game_control_handler.create_ongoing_action')
    async def test_controller_input_no_cancel_on_completed_action(self, mock_create_ongoing_action, mock_inferred_game_state):
        # Define a generator function for your responses
        def mock_inferred_game_state_responses():
            for _ in range(10):  # First 10 calls return in_match
                yield self.mock_in_match
            while True:  # Subsequent calls return in_menu infinitely
                yield self.mock_in_menu

        # Create a completed task
        completed_task = asyncio.create_task(asyncio.sleep(0))  # This task will complete immediately

        # Mock the create_ongoing_action function to return a completed task
        mock_create_ongoing_action.return_value = completed_task

        # Assign the async mock to read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Yield control back to the handler to let it run once
        await asyncio.sleep(0)

        # Assert that create_ongoing_action was called
        self.assertEqual(mock_create_ongoing_action.call_count, 1)

        # Allow a short wait for the transition to menu to take place
        await asyncio.sleep(0.01)

        # Ensure the task state is completed (not 'CANCELLED')
        self.assertEqual(mock_create_ongoing_action.return_value._state, 'FINISHED') 

        # Clean up
        self.shared_cleanup(handler_task)

    @patch('utilities.shared_thread_resources.inferred_game_state')
    async def test_controller_validate_input_received(self, mock_inferred_game_state):
        # Define a generator function for your responses
        def mock_inferred_game_state_responses():
            while True:  # Subsequent calls return in_menu infinitely
                yield self.mock_in_menu

        # Create an AsyncMock instance for read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())
        
        # Assign `AsyncMock` to read_data
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Yield control back to the handler to let it run once
        await asyncio.sleep(0.1)

        # Ensure the mock ongoing task was canceled
        self.game.io.tap.assert_called()

        # Clean up
        self.shared_cleanup(handler_task)

    @patch('utilities.shared_thread_resources.inferred_game_state')
    async def test_controller_game_input_received(self, mock_inferred_game_state):
        # Define a generator function for your responses
        def mock_inferred_game_state_responses():
            while True:  # Subsequent calls return in_menu infinitely
                yield self.mock_in_menu

        # Create an AsyncMock instance for read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())
        
        # Assign `AsyncMock` to read_data
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, self.game))

        # Yield control back to the handler to let it run once
        await asyncio.sleep(0.1)

        # Ensure the mock ongoing task was canceled
        self.game.io.tap.assert_called()

        # Clean up
        self.shared_cleanup(handler_task)

    @patch('utilities.shared_thread_resources.inferred_game_state')
    @patch('game_control_handler.create_ongoing_action')
    async def test_controller_navigates_sbc_navigates_next_opponent(self, mock_create_ongoing_action, mock_inferred_game_state):
        # Return mock inferred game state
        def mock_inferred_game_state_responses():
            state_length = 10
            for _ in range(state_length):  # First 10 calls return in_match
                yield self.mock_in_match
            for _ in range(state_length): # Then return 10 calls of in_menu
                yield self.mock_in_menu
            for _ in range(state_length): # Then return 10 calls of in_sbc_menu
                yield self.mock_in_menu_squad_battles_opponent_selection
            for _ in range(state_length): # Then return 10 calls of in_menu
                yield self.mock_in_menu
            while True:  # Subsequent calls return in_match infinitely
                yield self.mock_in_match

        # Create an AsyncMock instance for read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())

        # Assign the `AsyncMock` to read_data
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Use the real GameController class, but mock the input/output
        game_controller = GameController()
        game_controller.io = Mock(spec=PlaystationIO)
        game_controller.squad_battles_tracker.grid = [[True, False], [False, False]] # Mock the grid position
        # row, col should be at 0,0

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, game_controller))

        # Yield control back to the handler to let it run
        await asyncio.sleep(1)

        # Assert
        # We expect that during the squad_battles_opponent_selection state, the game controller will navigate
        # the SBC menu to the appropriate state
        self.assertEqual(game_controller.squad_battles_tracker.current_col, 1)
        self.assertEqual(game_controller.squad_battles_tracker.current_row, 0)
        self.assertEqual(game_controller.squad_battles_tracker.grid, [[True, True], [False, False]])
        
        # Assert that game_controller.io.tap was called in the correct order and with expected arguments
        expected_calls = [call(game_controller.io.Cross), call(game_controller.io.DPadRight)]
        game_controller.io.tap.assert_has_calls(expected_calls)

        # Clean up
        self.shared_cleanup(handler_task)

    @patch('utilities.shared_thread_resources.inferred_game_state')
    @patch('game_control_handler.create_ongoing_action')
    async def test_controller_navigates_sbc_play_match(self, mock_create_ongoing_action, mock_inferred_game_state):
        # Return mock inferred game state
        def mock_inferred_game_state_responses():
            state_length = 10
            for _ in range(state_length):  # First 10 calls return in_match
                yield self.mock_in_match
            for _ in range(state_length): # Then return 10 calls of in_menu
                yield self.mock_in_menu
            for _ in range(state_length): # Then return 10 calls of in_sbc_menu
                yield self.mock_in_menu_squad_battles_opponent_selection
            for _ in range(state_length): # Then return 10 calls of in_menu
                yield self.mock_in_menu
            while True:  # Subsequent calls return in_match infinitely
                yield self.mock_in_match

        # Create an AsyncMock instance for read_data
        async_mock_data_sequence = AsyncMock(side_effect=mock_inferred_game_state_responses())

        # Assign the `AsyncMock` to read_data
        mock_inferred_game_state.read_data = async_mock_data_sequence

        # Use the real GameController class, but mock the input/output
        game_controller = GameController()
        game_controller.io = Mock(spec=PlaystationIO)

        # Run the controller input handler
        handler_task = asyncio.create_task(controller_input_handler(self.app, game_controller))

        # Yield control back to the handler to let it run
        await asyncio.sleep(1)

        # Assert
        # We expect that during the squad_battles_opponent_selection state, the game controller will navigate
        # the SBC menu to the appropriate state
        self.assertEqual(game_controller.squad_battles_tracker.grid, [[True, False], [False, False]])
        game_controller.io.tap.assert_called_with(game_controller.io.Cross)

        # Clean up
        self.shared_cleanup(handler_task)

if __name__ == '__main__':
    unittest.main()
