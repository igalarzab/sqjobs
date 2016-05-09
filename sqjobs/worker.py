import sys
import traceback

from .exceptions import RetryException

import logging
logger = logging.getLogger('sqjobs.worker')


class Worker(object):
    DEFAULT_TIMEOUT = 20  # seconds

    def __init__(self, broker, queue_name, timeout=None):
        self.broker = broker
        self.queue_name = queue_name
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.registered_jobs = {}

    def __repr__(self):
        return 'Worker({connector})'.format(
            connector=type(self.broker.connector).__name__
        )

    def register_job(self, job_class):
        name = job_class._task_name()

        if job_class.abstract:
            logger.info('Job %s is abstract', name)
            return

        if name in self.registered_jobs:
            logger.warning('Job %s already registered, overwriting it...', name)

        self.registered_jobs[name] = job_class

    def run(self):
        for payload in self.broker.jobs(self.queue_name, self.timeout):
            try:
                job_class = self.registered_jobs.get(payload['name'])

                if not job_class:
                    logger.error('Unregistered task: %s', payload['name'])
                    continue

                job, args, kwargs = self.broker.unserialize_job(job_class, self.queue_name, payload)
                self._set_retry_time(job)
                self._execute_job(job, args, kwargs)
            except:
                logger.exception('Error executing job')

    def _set_retry_time(self, job):
        if job.next_retry_time() is None:  # Use default value of the queue
            return

        self.broker.set_retry_time(job, job.next_retry_time())

    def _execute_job(self, job, args, kwargs):
        try:
            job.execute(*args, **kwargs)
            self.broker.delete_job(job)
        except RetryException:
            job.on_retry()
            self.broker.retry(job)
            return
        except:
            job.on_failure()
            self._handle_exception(job, args, kwargs, *sys.exc_info())
            self.broker.retry(job)
            return

        job.on_success()

    def _handle_exception(self, job, args, kwargs, *exc_info):
        exception_message = ''.join(
            traceback.format_exception_only(*exc_info[:2]) +
            traceback.format_exception(*exc_info)
        )

        logger.error(exception_message, exc_info=True, extra={
            'job_queue_name': job.queue_name,
            'job_id': job.id,
            'job_name': job.name,
            'job_args': args,
            'job_kwargs': kwargs,
        })
