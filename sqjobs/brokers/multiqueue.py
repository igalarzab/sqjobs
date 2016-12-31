from time import time, sleep

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
        queue_last_check = {queue: 0 for queue in queue_names}

        # loop through the queue list forever
        while True:
            for queue in queue_names:
                next_check = queue_last_check[queue] + self.polling_interval

                # if it's been less than `polling_time` since last check, continue
                if next_check > int(time()):
                    continue

                # wait_time needs to be 0 or it will block in the first queue
                payload = self.connector.dequeue(queue, wait_time=0)
                if payload:
                    queue_last_check[queue] = 0
                    yield payload
                else:
                    queue_last_check[queue] = int(time())

            # only sleep if all queues are empty
            if all(value != 0 for value in queue_last_check.values()):
                sleep(self.polling_interval)
