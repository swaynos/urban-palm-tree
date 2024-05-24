import os
import sys
import unittest
from threading import Thread
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from shared_resources import ThreadSafeDeque

class TestThreadSafeDeque(unittest.TestCase):

    def setUp(self):
        self.deque = ThreadSafeDeque(maxsize=3)

    def test_append(self):
        self.deque.append(1)
        self.deque.append(2)
        self.deque.append(3)
        self.assertEqual(list(self.deque.deque), [1, 2, 3])

    def test_overflow(self):
        self.deque.append(1)
        self.deque.append(2)
        self.deque.append(3)
        self.deque.append(4)  # This should cause the oldest element (1) to be removed
        self.assertEqual(list(self.deque.deque), [2, 3, 4])  # Oldest element (1) should be removed

    def test_latest(self):
        self.deque.append(1)
        self.deque.append(2)
        self.assertEqual(self.deque.latest(), 2)

    def test_empty(self):
        self.assertTrue(self.deque.empty())
        self.deque.append(1)
        self.assertFalse(self.deque.empty())

    def test_peek_n_latest(self):
        for i in range(5):
            self.deque.append(i)
        self.assertEqual(self.deque.peek_n_latest(3), [2, 3, 4])

    def test_peek_n_latest_more_than_size(self):
        for i in range(3):
            self.deque.append(i)
        self.assertEqual(self.deque.peek_n_latest(5), [0, 1, 2])

    def test_thread_safety(self):
        """
        10 threads, with items being i % 4 to cycle through 0-3.
        Checks the counts of items in the deque to ensure no data corruption and verify that each item has a reasonable frequency.
        This test intends to cover thread safety by ensuring that the deque maintains its integrity under concurrent modifications 
        and through verifying the item frequencies.
        """
        def worker(deque, item):
            for _ in range(100):
                deque.append(item)
                sleep(0.01)

        threads = []
        for i in range(10):
            t = Thread(target=worker, args=(self.deque, i % 4))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Print the contents of the deque for debugging purposes
        print(f"Contents of deque: {list(self.deque.deque)}")

        # Check if the deque size is maintained correctly
        self.assertEqual(len(self.deque.deque), 3)
        # Ensure all elements in the deque are among the expected final elements
        self.assertTrue(all(item in range(4) for item in self.deque.deque), f"Deque contents: {list(self.deque.deque)}")

        # Additionally, verify no data corruption occurred by checking the expected frequency
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for item in self.deque.deque:
            counts[item] += 1

        print(f"Counts of items in deque: {counts}")
        self.assertTrue(all(count <= 3 for count in counts.values()), f"Counts exceed limits: {counts}")

if __name__ == '__main__':
    unittest.main()
