from .base import Connector


class Dummy(Connector):
    """
    Dummy connector for testing purposes
    """

    def __init__(self):
        self.jobs = {}
        self.deleted_jobs = {}
        self.retried_jobs = {}

        self.num_jobs = 0
        self.num_deleted_jobs = 0
        self.num_retried_jobs = 0

    def enqueue(self, queue_name, payload):
        self._get_queue(queue_name).append(payload)
        self.num_jobs += 1

    def dequeue(self, queue_name, wait_time=20):
        job = None

        try:
            job = self._get_queue(queue_name).pop()
            self.num_jobs -= 1
        except IndexError:
            pass

        return job

    def delete(self, queue_name, message_id):
        self.deleted_jobs.setdefault(queue_name, []).append(message_id)
        self.num_deleted_jobs += 1

    def set_retry_time(self, queue_name, message_id, delay):
        self.retried_jobs.setdefault(queue_name, []).append((message_id, delay))
        self.num_retried_jobs += 1

    def serialize_job(self, job_class, job_id, args, kwargs):
        return {
            'id': job_id,
            'name': job_class._task_name(),
            'args': args,
            'kwargs': kwargs
        }

    def unserialize_job(self, job_class, queue_name, payload):
        job = job_class()

        job.id = payload['id']
        job.queue_name = queue_name
        job.broker_id = payload['_metadata']['id']
        job.retries = payload['_metadata']['retries']
        job.created_on = payload['_metadata']['created_on']
        args = payload['args'] or []
        kwargs = payload['kwargs'] or {}

        return job, args, kwargs


    def _get_queue(self, name):
        return self.jobs.setdefault(name, [])
