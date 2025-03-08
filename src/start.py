import asyncio
import datetime
import logging
import signal

from controllers.game_strategy_controller import GameStrategyController
from utilities.shared_thread_resources import SharedProgramData
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

# Instantiate shared program data
shared_data = SharedProgramData()

# Begin Program
app = RunningApplication()
app.warm_up(config.APP_NAME)
game_flow = GameFlowController() 
game_strategy = GameStrategyController()

# Define sigint/sigterm handler
def exit_handler(signum, frame):
    signal_names = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM", signal.SIGSTOP: "SIGSTOP"}
    logging.critical(f"[{signal_names[signum]}] received. Application attempting to close gracefully.")
    
    # During exit these keys can become stuck.
    # The workaround is to press the stuck keys during an exit event.
    game_flow.io.press(game_flow.io.L2)
    game_flow.io.press(game_flow.io.Lstick.Up)
    game_flow.io.press(game_flow.io.Lstick.Left)
    shared_data.exit_event.set()
    
# Activate the handlers
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)

async def main():
    await asyncio.gather(
        capture_image_handler(app, shared_data),
        infer_image_handler(game_strategy, shared_data),
        controller_input_handler(app, game_flow, game_strategy, shared_data)
    )

if __name__ == "__main__":
    asyncio.run(main())