
# TODO: Unit Test is_point_in_bbox()
# Function to check if a point is within a bounding box
def is_point_in_bbox(point, bbox):
    x, y = point
    left, upper, right, lower = bbox
    return left <= x <= right and upper <= y <= lower