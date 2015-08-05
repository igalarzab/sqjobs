from .base import Broker

from uuid import uuid4


class Eager(Broker):

    def __repr__(self):
        return 'Broker(Eager)'

    def add_job(self, job_class, *args, **kwargs):
        job_id = str(uuid4())
        eager_job = job_class()
        eager_job.id = job_id
        try:
            eager_job.execute(*args, **kwargs)
            eager_job.on_success(*args, **kwargs)
        except Exception as e:
            eager_job.on_failure(e, *args, **kwargs)
        return job_id, eager_job
