from itertools import cycle

from .standard import Standard
from ..job import Job, JobResult


class MultiQueue(Standard):
    """
    Broker to execute jobs in an asynchronous way from multiple queues
    """
    def jobs(self, queue_names, timeout=20):
        for queue_name in cycle(queue_names):
            while True:
                payload = self.connector.dequeue(queue_name, wait_time=timeout)
                if payload or not timeout:
                    yield payload
                else:
                    break
