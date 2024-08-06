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
        grid (list): A 2x2 grid representing the state of matches.
        current_row (int): The current row index of the grid.
        current_col (int): The current column index of the grid.
        play_match_func (Optional[Callable[[int, int, list], None]]): A delegate function that can access the grid during play_match().
        navigate_func (Optional[Callable[[int, int, list], None]]): A delegate function that can access the grid during navigate_to_next().
        reset_grid_func (Optional[Callable[[], None]]): A delegate function that is called when grid is reset.

    Methods:
        __init__: Initializes the SquadBattlesTracker object.
        play_match: Marks the current match as played and navigates to the next match position.
        navigate_to_next: Updates the current row and column indices to move to the next match position.
        display_grid: Displays the current state of matches in the grid.
        set_grid: Sets the grid of the SquadBattlesTracker object.
    """
    def __init__(self, 
                 play_match_func: Optional[Callable[[int, int, list], None]] = None,
                 navigate_func: Optional[Callable[[int, int, list], None]] = None,
                 reset_grid_func: Optional[Callable[[], None]] = None):
        """
        Initializes the SquadBattlesTracker object.
        Parameters:
        play_match_func (Optional[Callable[[int, int, list], None]]): A delegate function that can access the grid during play_match().
        navigate_func (Optional[Callable[[int, int, list], None]]): A delegate function that can access the grid during navigate_to_next().
        reset_grid_func (Optional[Callable[[], None]]): A delegate function that is called when grid is reset.
        """
        self.grid = [[False, False], [False, False]]
        self.current_row = 0
        self.current_col = 0
        self.play_match_func = play_match_func
        self.navigate_func = navigate_func
        self.reset_grid_func = reset_grid_func

    def play_match(self):
        """
        Plays the current match if it hasn't been played yet.
        
        - If the grid is in its final state ([[True, True], [True, True]]), it will:
            - Call the `reset_grid_func` if it is provided.
            - Reset the grid to its default state.
            - Call itself recursively to play the first match.
        
        - If the current match at (current_row, current_col) hasn't been played:
            - It will call the `play_match_func` delegate with current_row, current_col, and grid as arguments.
            - Mark the current match as played.
            
        - If the current match at (current_row, current_col) has already been played:
            - It will navigate to the next match position.
            - Call the `play_match_func` delegate with updated current_row, current_col, and grid as arguments.
            - Mark the new current match as played.
        """
        if self.grid == [[True, True], [True, True]]:
            if self.reset_grid_func:
                self.reset_grid_func()
            self.set_grid()
            self.current_col = 0
            self.current_row = 0
            self.play_match()
        elif self.grid[self.current_row][self.current_col] == False:
            if self.play_match_func:
                self.play_match_func(self.current_row, self.current_col, self.grid)
            self.grid[self.current_row][self.current_col] = True
        elif self.grid[self.current_row][self.current_col] == True:
            self.navigate_to_next()
            if self.play_match_func:
                self.play_match_func(self.current_row, self.current_col, self.grid)
            self.grid[self.current_row][self.current_col] = True

    def navigate_to_next(self):
        """
        Update the current row and column indices to move to the next clockwise position in the 2x2 space.
        It will call the navigate_func delegate after updating current_row and current_col so that the 
        delegate function can understand where it is expected to be.
        The function navigates from the current match position to the next match position in the grid based on certain conditions:
        - If the current position is [X, 0] [0, 0], it moves to [0, X] [0, 0].
        - If the current position is [0, X] [0, 0], it moves to [0, 0] [X, 0].
        - If the current position is [0, 0] [0, X], it moves to [0, 0] [X, 0].
        - Otherwise, it resets the position to [0, 0] [0, 0].
        """
        if self.navigate_func:
            self.navigate_func(self.current_row, self.current_col, self.grid)
        # if [X, 0] [0, 0] -> [0, X] [0, 0]
        if self.current_col == 0 and self.current_row == 0:
            self.current_col += 1
        # elif [0, X] [0, 0] -> [0, 0] [X, 0]
        elif self.current_col == 1 and self.current_row == 0:
            self.current_row += 1
        # elif [0, 0] [0, X] -> [0, 0] [X, 0]
        elif self.current_col == 1 and self.current_row == 1:
            self.current_col = 0
        # else -> [0, 0] [0, 0]
        else:
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