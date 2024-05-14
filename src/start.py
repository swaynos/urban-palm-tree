import json
import logging
import requests
import signal
import threading
import time
from sys import platform

# urban-palm-tree imports
from shared_resources import exit_event, screenshots_stack, inferred_memory_stack
from capture_image_handler import capture_image_handler
from game_control_handler import controller_input_handler
from infer_image_handler import infer_image_handler
if platform == "darwin":
    from macos_app import RunningApplication
elif platform == "linux" or platform == "linux2":
    from linux_app import RunningApplication
from game_controller import GameController
import config

# Begin Program
app = RunningApplication()
if platform == "darwin":
    app.find_app(config.APP_NAME)
    app.activate_app()
    app.get_window()
elif platform == "linux" or platform == "linux2":
    app.find_window_by_name(config.APP_NAME)
    app.activate_window()

game = GameController()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a new Thread object for each function
capture_image_thread_instance = threading.Thread(target=capture_image_handler, args=(app,), name='capture_image_thread')
infer_image_thread_instance = threading.Thread(target=infer_image_handler, name='infer_image_thread')
controller_input_thread_instance = threading.Thread(target=controller_input_handler, args=(game,), name='controller_input_thread')
# TODO: another thread to read user input???

capture_image_thread_instance.start()
infer_image_thread_instance.start()
controller_input_thread_instance.start()

# Define sigint/sigterm handler
def exit_handler(signum, frame):
    signal_names = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM"}
    logging.critical(f"[{signal_names[signum]}] received. Application attempting to close gracefully.")
    if (signum == signal.SIGTERM):
        # During SIGTERM if the sleep duration is short (~1s) the ContextManager won't terminate gracefully.
        # This does not occur during SIGINT, so keeping it as a known issue for now. (Discovered in macos)
        # The workaround is to press the stuck keys during SIGTERM.
        game.io.press(game.io.L2)
        game.io.press(game.io.Lstick.Up)
        game.io.press(game.io.Lstick.Left)
    exit_event.set()
# Activate the handlers
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)

# Wait for threads to complete
capture_image_thread_instance.join()
infer_image_thread_instance.join()
controller_input_thread_instance.join()