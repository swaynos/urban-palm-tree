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
    def __init__(self):
        """
        Initializes the SquadBattlesTracker object.
        """
        self.grid = [[False, False], [False, False]]
        self.current_row = 0
        self.current_col = 0
        
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
            grid = [[False, False], [False, False]]
        self.grid = grid