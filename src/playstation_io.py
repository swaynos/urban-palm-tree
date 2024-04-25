from enum import Enum
from pynput import keyboard as kb

"""
Valid Keys
Buttons: Moon, Cross, Pyramid, Box, R1, L1, R3, L3, PS, Options, Touchpad, Share
D-Pad: Right, Down, Left, Up
Triggers: R2, L2
Sticks: Right Stick, Left Stick
"""
class Joystick():
     def __init__(self):
        self.Up = None
        self.Down = None
        self.Left = None
        self.Right = None
        

class PlaystationIO(kb.Controller):
    Moon = kb.Key.backspace
    Cross = kb.Key.enter
    Pyramid = kb.KeyCode(char='c')
    Box = kb.KeyCode(char='\\')
    DPadRight = kb.Key.right
    DPadDown = kb.Key.down
    DPadLeft = kb.Key.left
    DPadUp = kb.Key.up
    R1 = kb.KeyCode(char='3')
    L1 = kb.KeyCode(char='2')
    R3 = kb.KeyCode(char='6')
    L3 = kb.KeyCode(char='5')
    PS = kb.Key.esc
    Options = kb.KeyCode(char='o')
    Touchpad = kb.KeyCode(char='t')
    Share = kb.KeyCode(char='f')
    L2 = kb.KeyCode(char='1')
    R2 = kb.KeyCode(char='4')
    Lstick = Joystick()
    Rstick = Joystick()
    def __init__(self):
        super().__init__()
        self.Lstick.Left = kb.KeyCode(char='[')
        self.Lstick.Right = kb.KeyCode(char=']')
        self.Lstick.Up = kb.KeyCode(char='w')
        self.Lstick.Down = kb.KeyCode(char='s')
        self.Rstick.Left = kb.KeyCode(char='-')
        self.Rstick.Right = kb.KeyCode(char='=')
        self.Rstick.Down = kb.Key.page_down
        self.Rstick.Up = kb.Key.page_up

    """
    Release all joystick direction.
    
    Parameters:
    -----------
    joystick: Joystick, required
        The joystick to release all directions for.
    
    Returns:
    --------
    None
    """ 
    def release_joystick_direction(self, joystick):
        self.release(joystick.Down)
        self.release(joystick.Right)
        self.release(joystick.Left)
        self.release(joystick.Up)
    
    """
    Release all buttons on the controller.
    
    Returns:
    --------
    None
    """
    def release_all_buttons(self):
        self.release(self.Moon)
        self.release(self.Cross)
        self.release(self.Pyramid)
        self.release(self.Box)
        self.release(self.DPadRight)
        self.release(self.DPadDown)
        self.release(self.DPadLeft)
        self.release(self.DPadUp)
        self.release(self.R1)
        self.release(self.L1)
        self.release(self.R3)
        self.release(self.L3)
        self.release(self.PS)
        self.release(self.Options)
        self.release(self.Touchpad)
        self.release(self.Share)
        self.release(self.L2)
        self.release(self.R2)
        self.release_joystick_direction(self.Lstick)
        self.release_joystick_direction(self.Rstick)