import sys
import six

from .base import Broker


class Eager(Broker):

    def __repr__(self):
        return 'Broker(Eager)'

    def add_job(self, job_class, *args, **kwargs):
        job_id = self.gen_job_id()

        eager_job = job_class()
        eager_job.id = job_id

        try:
            eager_job.execute(*args, **kwargs)
            eager_job.on_success()
        except Exception as e:
            eager_job.on_failure()
            six.reraise(*sys.exc_info())

        return job_id
