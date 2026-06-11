import unittest
from unittest.mock import AsyncMock, MagicMock
from utilities.playstation_io import PlaystationIO
from game_action.action import Action
from pynput import keyboard as kb

from unittest.mock import AsyncMock, MagicMock, patch

class TestAction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.image_timestamp = 0.0
        self.infer_timestamp = 0.0
        self.playstation_io = AsyncMock(spec=PlaystationIO)
        self.steps = [
            ([kb.KeyCode.from_char('a'), kb.KeyCode.from_char('b')], 1.0),
            ([kb.KeyCode.from_char('x')], 0.5)
        ]
        self.action = Action(self.image_timestamp, self.infer_timestamp, self.playstation_io, self.steps)

    async def test_apply_steps(self):
        # We need to mock time.time only for execute_action_over_time called by apply_steps
        # Increment by 0.1 to ensure loop runs (duration 1.0 -> 10 iterations)
        with patch('game_action.action.time.time', side_effect=(i * 0.1 for i in range(1000))):
             await self.action.apply_steps()
        
        # Check interactions. Note: Execute_action_over_time calls hold_buttons (duration > 0).
        # In setup, duration is 1.0 and 0.5. Both > 0.
        # So execute_action_over_time is called.
        # So loop runs once.
        # Verify arguments
        self.playstation_io.hold_buttons.assert_any_call([kb.KeyCode.from_char('a'), kb.KeyCode.from_char('b')], 1.0)
        self.playstation_io.hold_buttons.assert_any_call([kb.KeyCode.from_char('x')], 0.5)

    async def test_execute_action(self):
        await self.action.execute_action([kb.KeyCode.from_char('a')])
        self.playstation_io.press_button.assert_called_once_with(kb.KeyCode.from_char('a'))

    async def test_execute_action_over_time(self):
        with patch('game_action.action.time.time', side_effect=(i * 0.1 for i in range(1000))):
            await self.action.execute_action_over_time([kb.KeyCode.from_char('a')], 1.0)
        self.playstation_io.hold_buttons.assert_called_with([kb.KeyCode.from_char('a')], 1.0)

    async def test_steps_to_string(self):
        result = await self.action.steps_to_string()
        expected = "Pressing keys: a, b for 1.0 seconds. Pressing keys: x for 0.5 seconds. "
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()