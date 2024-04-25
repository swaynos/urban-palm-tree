import time

from playstation_io import PlaystationIO

class GameController():
    def __init__(self):
        self.io = PlaystationIO()

    def go_to_corner(self, duration):
        # Hold L2 and go to the upper left corner of the screen
        with (self.io.pressed(self.io.L2, self.io.Lstick.Up, self.io.Lstick.Left)):
            time.sleep(duration)