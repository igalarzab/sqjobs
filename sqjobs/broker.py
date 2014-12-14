from .job import Job


class Broker(object):

    def __init__(self, connector):
        self.connector = connector

    def __repr__(self):
        return 'Broker({connector})'.format(
            connector=type(self.connector).__name__
        )

    def add_job(self, job, *args, **kwargs):
        if not issubclass(job, Job):
            raise ValueError('task must be a subclass of Job')

        payload = self._gen_job_payload(job, args, kwargs)
        self.connector.enqueue(job.queue, payload)

    def jobs(self, queue_name):
        while True:
            job = self.connector.dequeue(queue_name)

            if job:
                yield job

    def _gen_job_payload(self, job, args, kwargs):
        return {
            'name': job.name(),
            'args': args,
            'kwargs': kwargs
        }
