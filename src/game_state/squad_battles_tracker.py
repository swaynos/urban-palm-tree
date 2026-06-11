from typing import Callable, Optional

# 2 x 2 space grid
# 1st match: top left [1, 0] [0, 0]
# 2nd match: top right [1, 1] [0, 0]
# 3rd match: bottom right [1, 1] [1, 0]
# 4th match: bottom left [1, 1] [1, 1]
class SquadBattlesTracker:
    """
    A class that represents a 2x2 space grid for tracking matches in a squad battles game.

    Attributes:
        grid (list): A 2x2 grid representing the played state of matches.
        current_row (int): The current row index of the selection in the grid.
        current_col (int): The current column index of the selection in the grid.

    Methods:
        __init__: Initializes the SquadBattlesTracker object.
    """
    def __init__(self, play_match_func: Optional[Callable] = None, navigate_func: Optional[Callable] = None, reset_grid_func: Optional[Callable] = None):
        """
        Initializes the SquadBattlesTracker object.
        """
        self.grid = [[False, False], [False, False]]
        self.current_row = 0
        self.current_col = 0
        self.play_match_func = play_match_func
        self.navigate_func = navigate_func
        self.reset_grid_func = reset_grid_func
        
    def display_grid(self):
        """
        Display the current grid of matches with 'X' representing a match played and ' ' representing a match yet to be played.
        """
        for row in self.grid:
            display_row = ["X" if cell else " " for cell in row]
            print("[{}] [{}]".format(display_row[0], display_row[1]))
        print()

    def set_grid(self, grid: list[list[bool]] = None):
        """
        Set the grid of the SquadBattlesTracker object.

        Parameters:
        grid (list): A 2x2 grid representing the state of matches.

        If no grid is passed, the grid will be reset to [[False, False], [False, False]].
        """
        # Don't pass grid to reset the grid
        if (not grid):
            if self.reset_grid_func:
                self.reset_grid_func()
            grid = [[False, False], [False, False]]
        self.grid = grid

    def play_match(self):
        """
        Play the match at the current selection.
        """
        # If current match is already played, move to next
        if self.grid[self.current_row][self.current_col]:
            self.navigate_to_next()

        # Check reset condition (if all played, reset) 
        # CAUTION: Test `test_delegate_reset_grid_func_execution` expects reset when playing ON A FULL GRID?
        # Let's check that test again.
        # It sets grid to ALL TRUE.
        # Tracker at 1,0 (bottom left? No, 1,0 is bottom left in comments).
        # Calls play_match.
        # Expects: grid reset to False (except first one played?).
        # Expects: current 0,0.
        # Expects: grid[0][0] is True.
        
        # With "Search if occupied" logic:
        # Start: Grid all True. Cursor 1,0.
        # `if grid[1][0]: navigate()` -> moves to 0,0.
        # Now at 0,0. Grid[0][0] is True.
        # Recurse? Loop?
        # If I navigate once, I am at 0,0.
        # Grid[0][0] is True.
        # Should I navigate again?
        # If grid is FULL, I will loop forever if I keep navigating.
        # So I need to detect "All Played" before navigating?
        
        all_played = all(all(row) for row in self.grid)
        if all_played:
             self.set_grid() # Resets to False, False...
             self.current_row = 0
             self.current_col = 0
             # Now grid is empty. current is 0,0.
             # Proceed to play.
        
        # Now play
        if self.play_match_func:
             self.play_match_func(self.current_row, self.current_col, self.grid)

        self.grid[self.current_row][self.current_col] = True
        
        # Do NOT navigate at end.


    def navigate_to_next(self):
        """
        Navigate to the next match in the grid.
        """
        if self.navigate_func:
            self.navigate_func(self.current_row, self.current_col, self.grid)

        # Logic to move to the next logical match (row/col update)
        # Sequence: [0,0] -> [0,1] -> [1,1] -> [1,0] -> [0,0] (wraps or stays? Tests imply specific movement)
        
        # Based on test_play_match:
        # 1. Start 0,0. Play -> 0,0 marked. Next becomes 0,1.
        # 2. Play 0,1 -> 0,1 marked. Next becomes 1,1.
        # 3. Play 1,1 -> 1,1 marked. Next becomes 1,0.
        # 4. Play 1,0 -> 1,0 marked. Next becomes 0,0 again.
        
        if self.current_row == 0 and self.current_col == 0:
            self.current_row, self.current_col = 0, 1
        elif self.current_row == 0 and self.current_col == 1:
            self.current_row, self.current_col = 1, 1
        elif self.current_row == 1 and self.current_col == 1:
            self.current_row, self.current_col = 1, 0
        elif self.current_row == 1 and self.current_col == 0:
            self.current_row, self.current_col = 0, 0