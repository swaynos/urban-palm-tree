import asyncio
import datetime
import logging
import signal

from utilities.shared_thread_resources import exit_event
from handlers.capture_image_handler import capture_image_handler
from handlers.game_control_handler import controller_input_handler
from handlers.infer_image_handler import infer_image_handler

from utilities.macos_app import RunningApplication
from controllers.game_flow_controller import GameFlowController
import utilities.config as config

# Configure logging for the application
# Create a unique filename with a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f'start_{timestamp}.log'
logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_filename, filemode='w')

# Begin Program
app = RunningApplication()
app.warm_up(config.APP_NAME)
game = GameFlowController()         

# Define sigint/sigterm handler
def exit_handler(signum, frame):
    signal_names = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM", signal.SIGSTOP: "SIGSTOP"}
    logging.critical(f"[{signal_names[signum]}] received. Application attempting to close gracefully.")
    
    # During exit these keys can become stuck.
    # The workaround is to press the stuck keys during an exit event.
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
        infer_image_handler(game),
        controller_input_handler(app, game)
    )

if __name__ == "__main__":
    asyncio.run(main())