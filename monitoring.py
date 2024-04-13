import time

# Any code specific to monitoring the running python application should go here

# statistics
class Statistics:
    def __init__(self):
        self.count = 0
        self.start = time.time()

    def get_time(self):
        return time.time() - self.start