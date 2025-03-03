import unittest
from io import StringIO
import sys
from game_state.squad_battles_tracker import SquadBattlesTracker

class TestSquadBattlesTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = SquadBattlesTracker()

    def test_initial_grid(self):
        expected_grid = [[False, False], [False, False]]
        self.assertEqual(self.tracker.grid, expected_grid)
        self.assertEqual(self.tracker.current_row, 0)
        self.assertEqual(self.tracker.current_col, 0)

    def test_play_match(self):
        # Play the first match
        self.tracker.play_match()
        self.assertTrue(self.tracker.grid[0][0])
        self.assertEqual(self.tracker.current_row, 0)
        self.assertEqual(self.tracker.current_col, 0)
        
        # Play the second match
        self.tracker.play_match()
        self.assertTrue(self.tracker.grid[0][1])
        self.assertEqual(self.tracker.current_row, 0)
        self.assertEqual(self.tracker.current_col, 1)
        
        # Play the third match
        self.tracker.play_match()
        self.assertTrue(self.tracker.grid[1][1])
        self.assertEqual(self.tracker.current_row, 1)
        self.assertEqual(self.tracker.current_col, 1)
        
        # Play the fourth match
        self.tracker.play_match()
        self.assertTrue(self.tracker.grid[1][0])
        self.assertEqual(self.tracker.current_row, 1)
        self.assertEqual(self.tracker.current_col, 0)
        
        # Test playing an already played match
        self.tracker.play_match()
        self.assertTrue(self.tracker.grid[0][0])
        self.assertEqual(self.tracker.current_row, 0)
        self.assertEqual(self.tracker.current_col, 0)

    def test_navigate_to_next(self):
        # All play_match tests also test navigate_to_next indirectly
        self.tracker.navigate_to_next()
        self.assertEqual(self.tracker.current_col, 1)
        self.assertEqual(self.tracker.current_row, 0)
    
    def test_display_grid(self):
        captured_output = StringIO()
        sys.stdout = captured_output  # Redirect stdout
        
        # Initial grid display
        self.tracker.display_grid()
        self.assertEqual(captured_output.getvalue(), "[ ] [ ]\n[ ] [ ]\n\n")
        
        # Play some matches
        self.tracker.play_match()
        self.tracker.display_grid()
        self.assertEqual(captured_output.getvalue(), "[ ] [ ]\n[ ] [ ]\n\n[X] [ ]\n[ ] [ ]\n\n")
        
        self.tracker.play_match()
        self.tracker.display_grid()
        self.assertEqual(captured_output.getvalue()[len("[ ] [ ]\n[ ] [ ]\n\n[X] [ ]\n[ ] [ ]\n\n"):], "[X] [X]\n[ ] [ ]\n\n")
        
        self.tracker.play_match()
        self.tracker.display_grid()
        self.assertEqual(captured_output.getvalue()[len("[ ] [ ]\n[ ] [ ]\n\n[X] [ ]\n[ ] [ ]\n\n[X] [X]\n[ ] [ ]\n\n"):], "[X] [X]\n[ ] [X]\n\n")

        self.tracker.play_match()
        self.tracker.display_grid()
        self.assertEqual(captured_output.getvalue()[len("[ ] [ ]\n[ ] [ ]\n\n[X] [ ]\n[ ] [ ]\n\n[X] [X]\n[ ] [ ]\n\n[X] [X]\n[ ] [X]\n\n"):], "[X] [X]\n[X] [X]\n\n")
        sys.stdout = sys.__stdout__  # Reset redirect

    def test_set_grid_default(self):
        tracker = SquadBattlesTracker()
        tracker.set_grid()
        self.assertEqual(tracker.grid, [[False, False], [False, False]])

    def test_set_grid_custom(self):
        tracker = SquadBattlesTracker()
        custom_grid = [[True, False], [False, True]]
        tracker.set_grid(custom_grid)
        self.assertEqual(tracker.grid, custom_grid)

    def test_delegate_play_match_func_execution(self):
        executed = False

        def play_match_func(current_row, current_col, grid):
            nonlocal executed
            executed = True
            self.assertEqual(current_row, 0)
            self.assertEqual(current_col, 0)
            self.assertEqual(grid, [[False, False], [False, False]])  # Verify access to grid

        tracker = SquadBattlesTracker(play_match_func, None, None)

        # Play a match to trigger delegate function
        tracker.play_match()
        
        self.assertEqual(tracker.grid, [[True, False], [False, False]])  # Verify grid was updated

        self.assertTrue(executed)

    def test_delegate_navigate_func_execution(self):
        executed = False

        def navigate_func(current_row, current_col, grid):
            nonlocal executed
            executed = True
            self.assertEqual(current_row, 0)
            self.assertEqual(current_col, 0)
            self.assertEqual(grid, [[False, False], [False, False]])  # Verify access to grid

        tracker = SquadBattlesTracker(None, navigate_func, None)

        # Navigate to next to trigger delegate function
        tracker.navigate_to_next()
        
        self.assertEqual(tracker.current_row, 0)
        self.assertEqual(tracker.current_col, 1)
        self.assertTrue(executed)

    def test_delegate_reset_grid_func_execution(self):
        executed = False

        def reset_grid_func():
            nonlocal executed
            executed = True

        tracker = SquadBattlesTracker(None, None, reset_grid_func)
        
        # Set a full grid first
        tracker.set_grid([[True, True], [True, True]])
        tracker.current_col = 0
        tracker.current_row = 1
        
        # Play a match to trigger the reset delegate function
        tracker.play_match()
        
        self.assertEqual(tracker.grid, [[True, False], [False, False]])  # Verify grid was reset
        self.assertTrue(tracker.grid[0][0])
        self.assertEqual(tracker.current_row, 0)
        self.assertEqual(tracker.current_col, 0)
        self.assertTrue(executed)
       
if __name__ == "__main__":
    unittest.main()
