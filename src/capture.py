import asyncio

from handlers.capture_image_handler import capture_image_handler
from utilities.input_capture import on_press, on_release, on_click
from utilities.macos_app import RunningApplication
from utilities.shared_thread_resources import SharedProgramData

# Instantiate shared program data
shared_data = SharedProgramData()

# Start application
app = RunningApplication()

async def main():
    await capture_image_handler(app, shared_data)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        shared_data.exit_event.set()