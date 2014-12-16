import logging
logger = logging.getLogger('sqjobs.worker')


class Worker(object):

    def __init__(self, broker, queue_name):
        self.broker = broker
        self.queue_name = queue_name
        self.registered_jobs = {}

    def __repr__(self):
        return 'Worker({connector})'.format(
            connector=type(self.broker.connector).__name__
        )

    def register_job(self, job_class):
        name = job_class._task_name()

        if name in self.registered_jobs:
            logger.warning('Job %s already registered', name)

        self.registered_jobs[name] = job_class

    def execute(self):
        for payload in self.broker.jobs(self.queue_name):
            job, args, kwargs = self._build_job(payload)

            try:
                job.run(*args, **kwargs)
                self.broker.delete_job(job)
            except:
                logger.exception('Error executing job')
                self._change_retry_time(job)

    def _build_job(self, payload):
        job_class = self.registered_jobs.get(payload['name'])

        if not job_class:
            raise ValueError('Unregistered task: %s' % payload['name'])

        job = job_class()

        job.id = payload['_metadata']['id']
        job.retries = payload['_metadata']['retries']
        job.created_on = payload['_metadata']['created_on']
        job.first_execution_on = payload['_metadata']['first_execution_on']

        return job, payload['args'], payload['kwargs']

    def _change_retry_time(self, job):
        retry_time = job.next_retry()

        if retry_time:
            self.broker.set_retry_time(job, retry_time)
