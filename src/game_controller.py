import asyncio
import time
from typing import List

from game_state.squad_battles_tracker import SquadBattlesTracker
from playstation_io import PlaystationIO

class GameController():
    def __init__(self):
        self.time_delay = .1
        self.io = PlaystationIO()
        self.squad_battles_tracker = SquadBattlesTracker()
        self.squad_battles_tracker.play_match_func = self.play_match_function
        self.squad_battles_tracker.navigate_func = self.navigate_function
        self.squad_battles_tracker.reset_grid_func = self.reset_grid_function

    def play_match_function(self, row: int, col: int, grid: List[List[bool]]) -> None:
        self.io.tap(self.io.Cross)
        time.sleep(self.time_delay)

    def navigate_function(self, row: int, col: int, grid: List[List[bool]]) -> None:
        if (row, col) == (0, 0):
            self.io.tap(self.io.DPadRight)
        elif (row, col) == (0, 1):
            self.io.tap(self.io.DPadDown)
        elif (row, col) == (1, 1):
            self.io.tap(self.io.DPadLeft)
        elif (row, col) == (1, 0):
            self.io.tap(self.io.DPadUp)
        time.sleep(self.time_delay)

    def reset_grid_function(self) -> None:
        time.sleep(self.time_delay)

    def go_to_corner(self, duration):
        # Hold L2 and go to the upper left corner of the screen
        with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left):
            time.sleep(duration)
        self.io.tap(self.io.Cross)

    async def spin_in_circles(self, duration):
            end_time = time.time() + duration
            try:
                while time.time() < end_time:
                    # Sequence to spin in a circle
                    # Up and Left
                    with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left):
                        self.io.tap(self.io.Rstick.Left)
                        await asyncio.sleep(0.25)  # Keep it pressed for 0.25 seconds

                    # Up and Right
                    with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Right):
                        self.io.tap(self.io.Rstick.Left)
                        await asyncio.sleep(0.25)

                    # Down and Right
                    with self.io.pressed(self.io.L2, self.io.Lstick.Down, self.io.Lstick.Right):
                        self.io.tap(self.io.Rstick.Left)
                        await asyncio.sleep(0.25)

                    # Down and Left
                    with self.io.pressed(self.io.L2, self.io.Lstick.Down, self.io.Lstick.Left):
                        self.io.tap(self.io.Rstick.Left)
                        await asyncio.sleep(0.25)

                    # Back to Up and Left to complete the circle
                    with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left):
                        self.io.tap(self.io.Rstick.Left)
                        await asyncio.sleep(0.25)

            except asyncio.CancelledError:
                # Add any cleanup code if needed here when cancelled
                # This may be redundant
                self.io.release_joystick_direction(self.io.Lstick)
                self.io.release_joystick_direction(self.io.Rstick)
                # Notify about cancellation if needed
            finally:
                self.io.release_all_buttons() # Ensure all buttons are released
                pass