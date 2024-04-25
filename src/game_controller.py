from playstation_io import PlaystationIO

class GameController():
    def __init__(self):
        self.io = PlaystationIO()

    def go_to_corner(self):
        # Hold L2 and go to the upper left corner of the field
        self.io.press(PlaystationIO.L2)
        self.io.apply_joystick_direction(self.io.Lstick, 135)