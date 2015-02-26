from .base import Connector


class Dummy(Connector):
    """
    Dummy connector for test purposes
    """

    def __init__(self):
        self.jobs = {}
        self.deleted_jobs = {}
        self.retried_jobs = {}

        self.num_jobs = 0
        self.num_deleted_jobs = 0
        self.num_retried_jobs = 0

    def get_queue(self, name):
        return self.jobs.setdefault(name, [])

    def get_queues(self):
        return self.jobs.keys()

    def get_dead_letter_queues(self):
        return []

    def enqueue(self, queue_name, payload):
        self.get_queue(queue_name).append(payload)
        self.num_jobs += 1

    def dequeue(self, queue_name, wait_time=20):
        job = self.get_queue(queue_name).pop()
        self.num_jobs -= 1
        return job

    def delete(self, queue_name, message_id):
        self.deleted_jobs.setdefault(queue_name, []).append(message_id)
        self.num_deleted_jobs += 1

    def set_retry_time(self, queue_name, message_id, delay):
        self.retried_jobs.setdefault(queue_name, []).append((message_id, delay))
        self.num_retried_jobs += 1
