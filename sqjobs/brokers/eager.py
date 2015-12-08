import sys
import six

from uuid import uuid4

from .base import Broker


class Eager(Broker):

    def __repr__(self):
        return 'Broker(Eager)'

    def add_job(self, job_class, *args, **kwargs):
        eager_job = job_class()
        eager_job.id = str(uuid4())

        try:
            eager_job.execute(*args, **kwargs)
            eager_job.on_success(*args, **kwargs)
        except Exception as e:
            eager_job.on_failure(e, *args, **kwargs)
            six.reraise(*sys.exc_info())

        return job_id, eager_job
