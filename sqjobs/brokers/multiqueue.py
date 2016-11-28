from time import time, sleep
from itertools import cycle
from collections import defaultdict

from .standard import Standard


class MultiQueue(Standard):
    """
    Broker to execute jobs in an asynchronous way from multiple queues
    """
    polling_interval = 20  # seconds

    def jobs(self, queue_names, timeout=0):
        """
        * queue_names: List of queue names from where to read.
        * timeout: Not used by this implementation. It's kept for compatibility.
        """
        queue_last_check = defaultdict(int)

        for queue_name in cycle(queue_names):
            next_check = queue_last_check[queue_name] + self.polling_interval

            if next_check > int(time()):
                sleep(next_check - int(time()))

            while True:
                # wait_time needs to be 0 or it will block in the first queue
                payload = self.connector.dequeue(queue_name, wait_time=0)
                if payload:
                    yield payload
                else:
                    break

            queue_last_check[queue_name] = int(time())
