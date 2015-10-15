import sys
import traceback

from .job import RetryException

import logging
logger = logging.getLogger('sqjobs.worker')


class Worker(object):
    DEFAULT_TIMEOUT = 20

    def __init__(self, broker, queue_name, timeout=None):
        self.broker = broker
        self.queue_name = queue_name
        self.registered_jobs = {}
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def __repr__(self):
        return 'Worker({connector})'.format(
            connector=type(self.broker.connector).__name__
        )

    def register_job(self, job_class):
        name = job_class._task_name()

        if name in self.registered_jobs:
            logger.warning('Job %s already registered', name)

        if job_class.abstract:
            return

        self.registered_jobs[name] = job_class

    def execute_job(self, job, args, kwargs):
        try:
            self.broker.change_message_lock_timeout(job)
            job.execute(*args, **kwargs)
            self.broker.delete_job(job)
            job.on_success(*args, **kwargs)
        except RetryException:
            job.on_retry()
            self._change_retry_time(job)
        except:
            job.on_failure(*args, **kwargs)
            self._handle_exception(job, args, kwargs, *sys.exc_info())
            self._change_retry_time(job)

    def execute(self, forever=True):
        for payload in self.broker.jobs(self.queue_name, self.timeout, forever=forever):
            job, args, kwargs = self._build_job(payload)
            self.execute_job(job, args, kwargs)

    def _handle_exception(self, job, args, kwargs, *exc_info):
        exception_message = ''.join(
            traceback.format_exception_only(*exc_info[:2]) +
            traceback.format_exception(*exc_info)
        )

        logger.error(exception_message, exc_info=True, extra={
            'job_id': job.id,
            'job_name': job.name,
            'arguments': args,
            'kwarguments': kwargs,
            'queue_name': job.queue,
        })

    def _build_job(self, payload):
        job_class = self.registered_jobs.get(payload['name'])

        if not job_class:
            raise ValueError('Unregistered task: %s' % payload['name'])

        job = job_class()

        if 'job_id' in payload:
            job.id = payload['job_id']
        else:
            job.id = payload['_metadata']['id']

        job.queue = self.queue_name
        job.broker_id = payload['_metadata']['id']
        job.retries = payload['_metadata']['retries']
        job.created_on = payload['_metadata']['created_on']
        job.first_execution_on = payload['_metadata']['first_execution_on']
        args = payload['args'] or []
        kwargs = payload['kwargs'] or {}

        return job, args, kwargs

    def _change_retry_time(self, job):
        retry_time = job.next_retry()

        self.broker.retry(job, retry_time)
