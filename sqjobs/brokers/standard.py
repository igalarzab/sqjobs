from .base import Broker
from ..job import Job, JobResult


class Standard(Broker):
    """
    Standard broker to execute jobs in an asynchronous way
    """

    def __init__(self, connector):
        self.connector = connector

    def __repr__(self):
        return 'Broker({connector})'.format(
            connector=type(self.connector).__name__
        )

    def add_job(self, job_class, *args, **kwargs):
        job_id = self.gen_job_id()
        queue_name = kwargs.get('queue_name', job_class.default_queue_name)

        payload = self.serialize_job(job_class, job_id, args, kwargs)
        self.connector.enqueue(queue_name, payload)

        result = JobResult()
        result.job_id = job_id

        return result

    def delete_job(self, job):
        self.connector.delete(job.queue_name, job.broker_id)

    def retry(self, job):
        self.set_retry_time(job, 0)

    def set_retry_time(self, job, retry_time):
        self.connector.set_retry_time(job.queue_name, job.broker_id, retry_time)

    def jobs(self, queue_name, timeout=20):
        while True:
            payload = self.connector.dequeue(queue_name, wait_time=timeout)
            if payload or not timeout:
                yield payload
