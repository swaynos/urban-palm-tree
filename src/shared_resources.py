from asyncio import Event, Queue
from collections import deque
from threading import Lock

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
inferred_memory_collection = ThreadSafeDeque(maxsize=10)  # Replace 10 with the desired number of memories

# Event object for determining when the application is ready to exit
exit_event = Event()