import asyncio
import unittest
from utilities.shared_thread_resources import SharedObject

class TestSharedObject(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_initial_data_is_none(self):
        shared_obj = SharedObject()
        self.assertIsNone(shared_obj.data)

    def test_update_data(self):
        shared_obj = SharedObject()
        new_data = "New Data"
        self.loop.run_until_complete(shared_obj.update_data(new_data))
        self.assertEqual(shared_obj.data, new_data)

    def test_read_data(self):
        shared_obj = SharedObject()
        shared_obj.data = "Test Data"
        result = self.loop.run_until_complete(shared_obj.read_data())
        self.assertEqual(result, shared_obj.data)

if __name__ == '__main__':
    unittest.main()
