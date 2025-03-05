from asyncio import Event, Queue
from collections import deque
from threading import Lock

# TODO: Split file into package

import asyncio

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
    A singleton class that holds shared program data.
    This data is accessible across threads safely.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedProgramData, cls).__new__(cls)
            cls._instance.latest_screenshot = Queue(maxsize=1)
            cls._instance.inferred_memory_collection = ThreadSafeDeque(maxsize=10)  # Replace 10 with the desired number of memories
            cls._instance.inferred_game_state = SharedObject()
            cls._instance.exit_event = Event()
        return cls._instance
