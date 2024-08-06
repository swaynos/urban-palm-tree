import asyncio
import time

from game_state.squad_battles_tracker import SquadBattlesTracker
from playstation_io import PlaystationIO

class GameController():
    def __init__(self):
        self.io = PlaystationIO()
        self.squad_battles_tracker = SquadBattlesTracker()

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