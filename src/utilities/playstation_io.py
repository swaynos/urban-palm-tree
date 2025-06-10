import asyncio
import time
from typing import List
from pynput import keyboard as kb
from utilities import config

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

    async def press_button(self, button: kb.KeyCode, duration: float = 0.1):
        if config.CONTROLLER_INPUT_BYPASS:
            await asyncio.sleep(duration)
            return
        
        try:
            # Press the button
            self.tap(button)
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            # Handle cancellation if needed
            self.release(button)
        finally:
            self.release(button)  # Ensure the button is released at the end

    async def hold_buttons(self, buttons: List[kb.KeyCode], duration: float = 0.5):
        # When testing, it is preferred to bypass the controller input and instead simulate the delay
        if config.CONTROLLER_INPUT_BYPASS:
            await asyncio.sleep(duration)
            return
         
        try:
            with self.pressed(*buttons):
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            # Handle cancellation if needed
            for button in buttons:
                self.release(button)
        finally:
            # Ensure the buttons are released at the end
            for button in buttons:
                self.release(button)  

    # TODO: Come up with a better name for this method
    # This method can be re-used for multiple streams of input:
    # For example, while pressing the left joystick to upper left, I also want to tap
    # A every 50 ms, and then B every 200ms. How should that input be combined in a way 
    # where the syntax doesn't get too messy?
    # Note: two instances of this method can be run in parallel using asyncio.gather()
    async def do_something_long(self, duration):
        end_time = time.time() + duration
        try:
            while time.time() < end_time:
                # Just garbage input to show a couple of techniques using pynput
                with kb.Controller.pressed(kb.Key.shift, kb.KeyCode(char='\\')):
                    kb.Controller.tap(kb.Key.enter)
                    await asyncio.sleep(0.25)  # Keep it pressed for 0.25 seconds

        except asyncio.CancelledError:
            # Add any cleanup code if needed here when cancelled
            # Notify about cancellation if needed
            pass
        finally:
            self.release_all_buttons() # Ensure all buttons are released
            pass