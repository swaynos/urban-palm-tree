import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, call, patch
from game_state.game_state import GameState
from game_state.menu_state import MenuState
from handlers.game_control_handler import controller_input_handler
from controllers.game_flow_controller import GameFlowController
from controllers.game_strategy_controller import GameStrategyController
from utilities.macos_app import RunningApplication
from utilities.playstation_io import PlaystationIO
from utilities.shared_thread_resources import SharedProgramData

class TestGameControlHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Mock(spec=RunningApplication)
        self.game_flow = Mock(spec=GameFlowController)
        self.game_strategy = Mock(spec=GameStrategyController)
        self.shared_data = Mock(spec=SharedProgramData)
        self.shared_data.exit_event = asyncio.Event()
        self.shared_data.inference_completed_event = asyncio.Event()
        self.shared_data.inference_completed_event.clear = Mock()

    async def test_controller_input_loop(self):
        # Simulate ONE loop iteration
        # 1. shared_data.exit_event is NOT set initially
        # 2. handler calls build_actions
        # 3. handler calls execute_actions
        # 4. handler waits for inference_completed_event
        # 5. We trigger exit_event during the wait? Or after one loop?
        
        # Setup mocks
        self.game_flow.build_actions_from_strategy.return_value = []
        
        # We need to break the infinite loop.
        # Option: side_effect on inference_completed_event.wait which sets exit_event
        async def wait_side_effect():
            self.shared_data.exit_event.set()
        
        self.shared_data.inference_completed_event.wait = AsyncMock(side_effect=wait_side_effect)
        
        await controller_input_handler(self.app, self.game_flow, self.game_strategy, self.shared_data)
        
        # Verify calls
        self.game_flow.build_actions_from_strategy.assert_called_with(self.game_strategy)
        self.game_flow.execute_actions.assert_called_with([])
        self.shared_data.inference_completed_event.wait.assert_awaited()
        self.shared_data.inference_completed_event.clear.assert_called()

    @patch('game_action.action.time.time')
    @patch('handlers.game_control_handler.create_ongoing_action')
    async def test_real_game_flow_interaction(self, mock_create_ongoing_action, mock_time):
        # Mock time to increment to avoid busy wait loops in Action
        mock_time.side_effect = (i * 0.01 for i in range(1000000))
        # Test using REAL GameFlowController logic logic to verify SquadBattles integration
        # We need a real GameFlowController but MOCKED GameStrategy
        
        real_game_flow = GameFlowController()
        real_game_flow.io = AsyncMock(spec=PlaystationIO)
        # Configure buttons to avoid Action logging crash
        real_game_flow.io.Cross = Mock()
        real_game_flow.io.Cross.char = 'x'
        real_game_flow.io.DPadRight = Mock()
        real_game_flow.io.DPadRight.char = 'right'
        real_game_flow.io.DPadLeft = Mock()
        real_game_flow.io.DPadLeft.char = 'left'
        real_game_flow.io.DPadUp = Mock()
        real_game_flow.io.DPadUp.char = 'up'
        real_game_flow.io.DPadDown = Mock()
        real_game_flow.io.DPadDown.char = 'down'

        # Setup strategy to return SQUAD_BATTLES_OPPONENT_SELECTION
        self.game_strategy.get_strategic_intent.return_value = None
        self.game_strategy.get_menu_state.return_value = MenuState.SQUAD_BATTLES_OPPONENT_SELECTION
        # Mock timestamps
        self.game_strategy.last_image = Mock()
        self.game_strategy.last_image.get_timestamp.return_value = 100.0
        self.game_strategy.image_inference_timestamp = 101.0
        
        # Setup tracker in real_game_flow
        # Default tracker starts at 0,0.
        # verify initial state
        self.assertEqual(real_game_flow.squad_battles_tracker.current_row, 0)
        self.assertEqual(real_game_flow.squad_battles_tracker.current_col, 0)
        # Mark 0,0 as already played so play_match navigates to 0,1
        real_game_flow.squad_battles_tracker.grid[0][0] = True
        
        # Run ONE iteration of loop logic manually (simulating handler)
        actions = await real_game_flow.build_actions_from_strategy(self.game_strategy)
        
        # Verify logic:
        # 1. Tracker should have updated (played 0,0) -> moved to 0,1.
        self.assertEqual(real_game_flow.squad_battles_tracker.current_col, 1) # Next is 0,1
        self.assertEqual(real_game_flow.squad_battles_tracker.current_row, 0)
        
        # 2. Actions generated
        # Expect: Cross (Select), DPadRight (Navigate 0->1)
        self.assertEqual(len(actions), 2)
        # Check timestamps and buttons
        # Note: action structure is complex, we can check calls on io if we executed them?
        # But we only built them.
        # Let's inspect actions.
        # Action 1: Cross
        # Key presses in action steps.
        # We assume get_action_from_button works.
        
        # To verify interactions with IO, we should execute them.
        await real_game_flow.execute_actions(actions)
        
        # Verify IO calls
        # Cross pressed. DPadRight pressed.
        # Order matters? execute_actions executes in order.
        expected_calls = [
            call([real_game_flow.io.Cross], 0.1),
            call([real_game_flow.io.DPadRight], 0.1)
        ]
        # hold_buttons is called by action.apply_steps -> execute_action_over_time -> io.hold_buttons
        # wait. get_action_from_button uses duration.
        # Default duration 0.1 provided in code.
        # So it calls hold_buttons or press_button?
        # Action implementation: if duration > 0 -> hold_buttons. if == 0 -> press_button.
        
        # Let's verify hold_buttons called.
        self.assertTrue(real_game_flow.io.hold_buttons.called)
        
        # Also verify tap was NOT called (unless duration 0)
        
    @patch('game_action.action.time.time')
    async def test_sbc_navigation_logic_wrapping(self, mock_time):
        # Mock time to increment to avoid busy wait loops in Action
        mock_time.side_effect = (i * 0.01 for i in range(1000000))
        # Test wrapping/movement logic
        real_game_flow = GameFlowController()
        real_game_flow.io = AsyncMock(spec=PlaystationIO)
        # Configure buttons to avoid Action logging crash
        real_game_flow.io.Cross = Mock()
        real_game_flow.io.Cross.char = 'x'
        real_game_flow.io.DPadRight = Mock()
        real_game_flow.io.DPadRight.char = 'right'
        real_game_flow.io.DPadLeft = Mock()
        real_game_flow.io.DPadLeft.char = 'left'
        real_game_flow.io.DPadUp = Mock()
        real_game_flow.io.DPadUp.char = 'up'
        real_game_flow.io.DPadDown = Mock()
        real_game_flow.io.DPadDown.char = 'down'
        
        # Set tracker to 0,1 (Top Right)
        real_game_flow.squad_battles_tracker.current_row = 0
        real_game_flow.squad_battles_tracker.current_col = 1
        real_game_flow.squad_battles_tracker.grid[0][0] = True # Top left played
        real_game_flow.squad_battles_tracker.grid[0][1] = True # Top right played, so play_match navigates to 1,1
        
        self.game_strategy.get_strategic_intent.return_value = None
        self.game_strategy.get_menu_state.return_value = MenuState.SQUAD_BATTLES_OPPONENT_SELECTION
        self.game_strategy.last_image = Mock()
        self.game_strategy.last_image.get_timestamp.return_value = 100.0
        self.game_strategy.image_inference_timestamp = 101.0
        
        # Build actions
        actions = await real_game_flow.build_actions_from_strategy(self.game_strategy)
        
        # Logic: Play 0,1. Move to 1,1.
        # Expect: Cross. DPadDown?
        # 0,1 -> 1,1. Col same. Row 0 -> 1 (Down).
        
        await real_game_flow.execute_actions(actions)
        
        # Check IO
        # Cross
        # DPadDown
        self.assertTrue(real_game_flow.io.hold_buttons.called)
        
        # Verify tracker updated
        self.assertEqual(real_game_flow.squad_battles_tracker.current_row, 1)
        self.assertEqual(real_game_flow.squad_battles_tracker.current_col, 1)

if __name__ == '__main__':
    unittest.main()
