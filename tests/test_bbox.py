# test_bbox.py
import unittest
from utilities.bbox import is_point_in_bbox

class TestIsPointInBbox(unittest.TestCase):

    def test_point_inside_bbox(self):
        point = (5, 5)
        bbox = (0, 0, 10, 10)
        self.assertTrue(is_point_in_bbox(point, bbox))

    def test_point_on_left_edge(self):
        point = (0, 5)
        bbox = (0, 0, 10, 10)
        self.assertTrue(is_point_in_bbox(point, bbox))

    def test_point_on_right_edge(self):
        point = (10, 5)
        bbox = (0, 0, 10, 10)
        self.assertTrue(is_point_in_bbox(point, bbox))

    def test_point_on_upper_edge(self):
        point = (5, 0)
        bbox = (0, 0, 10, 10)
        self.assertTrue(is_point_in_bbox(point, bbox))

    def test_point_on_lower_edge(self):
        point = (5, 10)
        bbox = (0, 0, 10, 10)
        self.assertTrue(is_point_in_bbox(point, bbox))

    def test_point_outside_bbox(self):
        point = (11, 5)
        bbox = (0, 0, 10, 10)
        self.assertFalse(is_point_in_bbox(point, bbox))

    def test_point_below_bbox(self):
        point = (5, -1)
        bbox = (0, 0, 10, 10)
        self.assertFalse(is_point_in_bbox(point, bbox))

    def test_point_above_bbox(self):
        point = (5, 11)
        bbox = (0, 0, 10, 10)
        self.assertFalse(is_point_in_bbox(point, bbox))

if __name__ == "__main__":
    unittest.main()