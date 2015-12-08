from uuid import uuid4

from .base import Broker
from ..job import Job


class Standard(Broker):
    def __init__(self, connector):
        self.connector = connector

    def __repr__(self):
        return 'Broker({connector})'.format(
            connector=type(self.connector).__name__
        )

    def add_job(self, job_class, *args, **kwargs):
        job_id = str(uuid4())
        queue_name = kwargs.get('queue_name', job_class.default_queue_name)

        payload = self.serialize_job(job_class, job_id, args, kwargs)
        self.connector.enqueue(queue_name, payload)

        return job_id

    def delete_job(self, job):
        self.connector.delete(job.queue_name, job.broker_id)

    def retry(self, job):
        self.connector.retry(job.queue_name, job.broker_id, job.next_retry_time())

    def jobs(self, queue_name, timeout=20):
        while True:
            payload = self.connector.dequeue(queue_name, wait_time=timeout)
            if payload or not timeout:
                yield payload

    def serialize_job(self, job_class, job_id, args, kwargs):
        return self.connector.serialize_job(job_class, job_id, args, kwargs)

    def unserialize_job(self, job_class, queue_name, payload):
        return self.connector.unserialize_job(job_class, queue_name, payload)
