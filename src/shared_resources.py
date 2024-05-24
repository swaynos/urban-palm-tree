from queue import LifoQueue, Queue
from threading import Lock

class ThreadSafeDeque(LifoQueue):
    """
    A custom class for the queue that provides thread-safe operations for clearing the oldest elements. 
    The LifoQueue from the queue module already provides thread safety for basic operations, 
    but we'll extend it to handle custom clearing logic.
    """
    def __init__(self, max_size):
        super().__init__(maxsize=max_size)
        self.lock = Lock()

    def append(self, item):
        with self.lock:
            if self.full():
                self.get()  # Remove the oldest element (bottom of the stack)
            self.put(item)

    def latest(self):
        with self.lock:
            return self.queue[-1] if not self.empty() else None

    def get_n_latest(self, n):
        with self.lock:
            return list(self.queue)[-n:] if n <= self.qsize() else list(self.queue)

# Resources shared across all tasks
latest_screenshot = Queue(maxsize=1)
inferred_memory_collection = ThreadSafeDeque(max_size=10)  # Replace 10 with the desired number of memories