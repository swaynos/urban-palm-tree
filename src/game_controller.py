import time

from playstation_io import PlaystationIO

class GameController():
    instructions = []
    
    def __init__(self):
        self.io = PlaystationIO()

    def go_to_corner(self, duration):
        # Hold L2 and go to the upper left corner of the screen
        with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left):
            time.sleep(duration)
        self.io.tap(self.io.Cross)

    def spin_in_circles(self, duration):
        # Hold L2 and spin in a circle
        with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left):
            time.sleep(duration / 4)
        with self.io.pressed(self.io.L2, self.io.Lstick.Down, self.io.Lstick.Left):
            time.sleep(duration / 4)
        with self.io.pressed(self.io.L2, self.io.Lstick.Down, self.io.Lstick.Right):
            time.sleep(duration / 4)
        with self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Right):
            time.sleep(duration / 4)