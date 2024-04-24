from enum import Enum
from pynput import keyboard as kb

import pynput

"""
Valid Keys
Buttons: Moon, Cross, Pyramid, Box, R1, L1, R3, L3, PS, Options, Touchpad, Share
D-Pad: Right, Down, Left, Up
Triggers: R2, L2
Sticks: Right Stick, Left Stick
"""
class Joystick(Enum):
    Up = 1
    Down = 2
    Left = 3
    Right = 4

class PlaystationController(kb.Controller):
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
    Lstick = Joystick
    Rstick = Joystick
    def __init__(self):
        super().__init__()
    