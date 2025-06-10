import unittest
from unittest.mock import AsyncMock, MagicMock
from utilities.playstation_io import PlaystationIO
from game_action.action import Action
from pynput import keyboard as kb

class TestAction(unittest.TestCase):
    def setUp(self):
        self.image_timestamp = 0.0
        self.infer_timestamp = 0.0
        self.playstation_io = MagicMock(spec=PlaystationIO)
        self.steps = [
            ([kb.KeyCode.from_char('a'), kb.KeyCode.from_char('b')], 1.0),
            ([kb.KeyCode.from_char('x')], 0.5)
        ]
        self.action = Action(self.image_timestamp, self.infer_timestamp, self.playstation_io, self.steps)

    async def test_apply_steps(self):
        await self.action.apply_steps()
        self.assertEqual(self.playstation_io.press_button.call_count, 3)  # a, b, x
        self.playstation_io.press_button.assert_any_call(kb.KeyCode.from_char('a'))
        self.playstation_io.press_button.assert_any_call(kb.KeyCode.from_char('b'))
        self.playstation_io.press_button.assert_any_call(kb.KeyCode.from_char('x'))

    async def test_execute_action(self):
        await self.action.execute_action([kb.KeyCode.from_char('a')])
        self.playstation_io.press_button.assert_called_once_with(kb.KeyCode.from_char('a'))

    async def test_execute_action_over_time(self):
        await self.action.execute_action_over_time([kb.KeyCode.from_char('a')], 1.0)
        self.playstation_io.hold_buttons.assert_called_once_with([kb.KeyCode.from_char('a')], 1.0)

    async def test_steps_to_string(self):
        result = await self.action.steps_to_string()
        expected = "Pressing keys: a, b for 1.0 seconds. Pressing keys: x for 0.5 seconds. "
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()