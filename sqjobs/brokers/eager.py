import sys
import six

from .base import Broker
from ..job import JobResult


class Eager(Broker):
    """
    Broker to execute jobs in a synchronous way
    """

    def __repr__(self):
        return 'Broker(Eager)'

    def add_job(self, job_class, *args, **kwargs):
        job_id = self.gen_job_id()

        eager_job = job_class()
        eager_job.id = job_id

        try:
            result = eager_job.execute(*args, **kwargs)
            eager_job.on_success()
        except Exception as e:
            eager_job.on_failure()
            six.reraise(*sys.exc_info())

        job_result = JobResult()
        job_result.job_id = job_id
        job_result.result = result

        return job_result
