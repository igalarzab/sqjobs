from .base import Broker


class Eager(Broker):

    def __repr__(self):
        return 'Broker(Eager)'

    def add_job(self, job_class, *args, **kwargs):
        import time
        eager_job = job_class()
        eager_job.id = '%s' % time.time()
        try:
            eager_job.execute(*args, **kwargs)
            eager_job.on_success(*args, **kwargs)
        except Exception as e:
            eager_job.on_failure(e, *args, **kwargs)
        return eager_job
