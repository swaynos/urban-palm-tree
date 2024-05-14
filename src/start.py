import asyncio
import logging
import signal
import threading
from sys import platform

# urban-palm-tree imports
from shared_resources import exit_event
from capture_image_handler import capture_image_handler
from game_control_handler import controller_input_handler
from infer_image_handler import infer_image_handler
if platform == "darwin":
    from macos_app import RunningApplication
elif platform == "linux" or platform == "linux2":
    from linux_app import RunningApplication
from game_controller import GameController
import config

# configure logging for the application
logging.basicConfig(level="DEBUG") # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

async def main():
    await asyncio.gather(
        capture_image_handler(app),
        infer_image_handler(),
        controller_input_handler(game)
    )

if __name__ == "__main__":
    asyncio.run(main())