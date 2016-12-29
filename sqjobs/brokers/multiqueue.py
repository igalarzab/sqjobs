from time import time
from itertools import cycle
from collections import defaultdict

from .standard import Standard


class MultiQueue(Standard):
    """
    Broker to execute jobs in an asynchronous way from multiple queues.
    Execute a job from one queue and go to the next one, if the queue is empty
    add a timestamp to wait `polling_interval` seconds before trying again.
    """
    polling_interval = 20  # seconds

    def jobs(self, queue_names, timeout=0):
        """
        * queue_names: List of queue names from where to read.
        * timeout: Not used by this implementation. It's kept for compatibility.
        """
        queue_last_check = defaultdict(int)

        # loop through the queue list forever
        for queue_name in cycle(queue_names):
            next_check = queue_last_check[queue_name] + self.polling_interval

            if next_check > int(time()):
                continue

            # wait_time needs to be 0 or it will block in the first queue
            payload = self.connector.dequeue(queue_name, wait_time=0)
            if payload:
                yield payload
            else:
                # only update last check when queue is empty
                queue_last_check[queue_name] = int(time())
