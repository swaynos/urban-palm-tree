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


# Resources shared across all tasks
latest_screenshot = Queue(maxsize=1)
"""
A queue to hold the most recent screenshot to be processed for inference.

This queue has a maximum size of 1, ensuring that it can only store
the latest screenshot. If a new screenshot is added when the queue
is full, the oldest screenshot will be discarded.
"""

latest_actions_sequence = Queue(maxsize=1)
"""
A queue to hold the most recent sequence of actions.

This queue has a maximum size of 1, ensuring that it can only store
the latest sequence of actions. If a new action sequence is added 
when the queue is full, the oldest sequence will be discarded, allowing 
the system to retain only the most current actions for processing.
"""

# Event object for determining when the application is ready to exit
exit_event = Event()