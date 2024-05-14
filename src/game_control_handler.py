import logging
import monitoring

from game_controller import GameController
from shared_resources import exit_event, inferred_memory_stack

controller_input_thread_statistics = monitoring.Statistics()

def controller_input_handler(game: GameController):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    while(not exit_event.is_set()):
        try:
            # TODO: Only enter if the right window is active. (Annoying that keystrokes are entered while debugging)
            logging.debug(f"controller_input_thread: Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
            
            memory = None
            if (not inferred_memory_stack.empty()):
                memory = inferred_memory_stack._queue[-1]
            
            if memory == "IN-MATCH":
                # press, release, tap to send input to the controller. Joystick movement is special.
                logging.info("controller_input_thread: grabbing closest player and spinning in a circle")
                game.io.tap(game.io.L1)
                game.spin_in_circles(3)
            elif memory == "IN-MENU":
                logging.info("controller_input_thread: tapping cross")
                game.io.tap(game.io.Cross)
            
            controller_input_thread_statistics.count += 1
        except Exception as argument:
            logging.error(argument)