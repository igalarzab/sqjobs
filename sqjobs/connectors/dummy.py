from .base import Connector


class Dummy(Connector):
    """
    Dummy connector for test purposes
    """

    def __init__(self):
        self.jobs = {}
        self.num_jobs = 0

    def create_queue(self, name):
        raise NotImplementedError

    def delete_queue(self, name):
        raise NotImplementedError

    def get_queue(self, name):
        raise NotImplementedError

    def enqueue(self, queue_name, payload):
        self.jobs.setdefault(queue_name, []).append(payload)
        self.num_jobs += 1

    def dequeue(self, queue_name, wait_time=20):
        raise NotImplementedError

    def delete(self, queue_name, message_id):
        raise NotImplementedError

    def set_retry_time(self, queue_name, message_id, delay):
        raise NotImplementedError
