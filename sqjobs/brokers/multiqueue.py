from itertools import cycle

from .standard import Standard
from ..job import Job, JobResult


class MultiQueue(Standard):
    """
    Broker to execute jobs in an asynchronous way from multiple queues
    """
    def jobs(self, queue_names, timeout=0):
        """
        * queue_names: List of queue names from where to read.
        * timeout: Not used by this implementation. It's kept for compatibility.
        """
        for queue_name in cycle(queue_names):
            while True:
                # wait_time needs to be 0 or it will block on the first queue
                payload = self.connector.dequeue(queue_name, wait_time=0)
                if payload:
                    yield payload
                else:
                    break
