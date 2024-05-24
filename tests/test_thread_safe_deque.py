import os
import sys
import unittest
from threading import Thread
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from shared_resources import ThreadSafeDeque

class TestThreadSafeDeque(unittest.TestCase):
    def setUp(self):
        self.deque = ThreadSafeDeque(max_size=3)

    def test_append(self):
        self.deque.append(1)
        self.deque.append(2)
        self.deque.append(3)
        self.assertEqual(self.deque.queue, [1, 2, 3])

    def test_overflow(self):
        self.deque.append(1)
        self.deque.append(2)
        self.deque.append(3)
        self.deque.append(4)
        self.assertEqual(self.deque.queue, [2, 3, 4])  # Oldest element (1) should be removed

    def test_latest(self):
        self.deque.append(1)
        self.deque.append(2)
        self.assertEqual(self.deque.latest(), 2)

    def test_get_n_latest(self):
        self.deque.append(1)
        self.deque.append(2)
        self.deque.append(3)
        self.assertEqual(self.deque.get_n_latest(2), [2, 3])

    def test_thread_safety(self):
        def worker(deque, item):
            for _ in range(100):
                deque.append(item)
                sleep(0.01)

        threads = []
        for i in range(4):
            t = Thread(target=worker, args=(self.deque, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Check if the deque size is maintained correctly and the last elements are from the last threads
        self.assertEqual(len(self.deque.queue), 3)
        self.assertTrue(all(item in range(1, 4) for item in self.deque.queue))

if __name__ == '__main__':
    unittest.main()
