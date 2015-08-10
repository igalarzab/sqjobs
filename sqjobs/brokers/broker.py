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
        if not issubclass(job_class, Job):
            raise ValueError('task must be a subclass of Job')

        job_id = str(uuid4())
        payload = self._gen_job_payload(job_id, job_class, args, kwargs)
        response = self.connector.enqueue(job_class.queue, payload)
        return job_id, response

    def jobs(self, queue_name, timeout=0, nowait=False, forever=True):
        at_least_once = True
        while at_least_once or forever:
            at_least_once = False
            payload = self.connector.dequeue(queue_name, wait_time=timeout)
            if payload or nowait:
                yield payload

    def queues(self):
        return self.connector.get_queues()

    def dead_letter_queues(self):
        return self.connector.get_dead_letter_queues()

    def change_message_lock_timeout(self, job):
        """
        Lock timeout uses the same amount of time than retry but with different
        purposes.

        Lock read timeout is used to extend the time the message is locked because
        for example the job duration is beyond the default lock value.
        In the retry case the lock time is used to hide the message until the
        retry time passed and other worker use it to retry the job
        """
        if job.lock_time:
            self.connector.retry(job.queue, job.broker_id, job.lock_time)

    def delete_job(self, job):
        self.delete_message(job.queue, job.broker_id)

    def delete_message(self, queue, message_id):
        self.connector.delete(queue, message_id)

    def retry(self, job, delay=None):
        self.connector.retry(job.queue, job.broker_id, delay)

    def _gen_job_payload(self, job_id, job_class, args, kwargs):
        return {
            'job_id': job_id,
            'name': job_class._task_name(),
            'args': args,
            'kwargs': kwargs
        }
