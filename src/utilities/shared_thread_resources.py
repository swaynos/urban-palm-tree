import asyncio

from asyncio import Event, Queue
from collections import deque
from threading import Lock
from inference.yolo_object_detector import YoloObjectDetector
from utilities import config

# TODO: Split file into package. Each class requires it's own file.

class SharedObject:
    """
    A class representing a shared object with a lock for thread safety. 
    Allows updating and reading data in a thread-safe manner.

    Attributes:
    - data: The shared data stored in the object.
    - lock: A lock object for synchronization.

    Methods:
    - update_data(new_data): Updates the shared data with new_data.
    - read_data(): Reads and returns the current shared data.
    """
    def __init__(self):
        self.data = None
        self.lock = asyncio.Lock()

    async def update_data(self, new_data):
        async with self.lock:
            self.data = new_data

    async def read_data(self):
        async with self.lock:
            return self.data


class ThreadSafeDeque:
    """
    A custom class for a deque that provides thread-safe operations for appending items and
    peeking at the last elements.
    """
    def __init__(self, maxsize):
        self.deque = deque(maxlen=maxsize)
        self.lock = Lock()

    def append(self, item):
        with self.lock:
            self.deque.append(item)  # Append will automatically discard the oldest if deque is full

    def latest(self):
        with self.lock:
            return self.deque[-1] if self.deque else None

    def empty(self):
        with self.lock:
            return len(self.deque) == 0

    def peek_n_latest(self, n):
        with self.lock:
            return list(self.deque)[-n:] if n <= len(self.deque) else list(self.deque)

# Resources shared across all tasks.
class SharedProgramData:
    """
    A multiprocessing-safe singleton using CUDA preloading.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedProgramData, cls).__new__(cls)
            cls._instance.latest_screenshot = Queue(maxsize=1)
            cls._instance.exit_event = Event()

            # Initialize CUDA once in the main process
            if torch.cuda.is_available():
                print("[Main] Initializing CUDA once...")
                torch.cuda.init()
                torch.cuda.synchronize()

            # Load YOLO model into CUDA memory only once
            print("[Main] Loading YOLO model onto GPU...")
            # TODO: Test and evaluate whether having the initialize code in here is necessary
            cls._instance.rush_detection_model = YoloObjectDetector(config.HF_RUSH_DETECTION_PATH, config.HF_RUSH_DETECTION_FILENAME)
            cls._instance.rush_detection_model.model.to("cuda")  # Load onto GPU
            torch.cuda.synchronize()
            print("[Main] YOLO model loaded and CUDA ready.")

        return cls._instance
