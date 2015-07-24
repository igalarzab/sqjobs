import time
import json
from datetime import datetime, timedelta
from pytz import timezone
import logging

from django.db import transaction

from .models import PeriodicJob

logger = logging.getLogger('sqjobs.beat')


class Beat(object):

    def __init__(self, broker, sleep_interval=10, skip_delayed_jobs=None):
        self.broker = broker
        self.sleep_interval = sleep_interval
        self.currently_expired_jobs = []
        self.skip_delayed_jobs = skip_delayed_jobs

    def get_class_and_kwargs(self, job):
        m_name, c_name = job.task.rsplit('.', 1)
        import importlib
        m = importlib.import_module(m_name)
        job_class = getattr(m, c_name)
        kwargs = json.loads(job.args)
        kwargs[PeriodicJob.PROGRAMMED_DATE] = job.next_execution.isoformat()
        return job_class, kwargs

    def get_expired_jobs(self):
        try:
            self.currently_expired_jobs = PeriodicJob.objects.filter(
                enabled=True,
                next_execution__lte=datetime.utcnow(),
            )
        except PeriodicJob.DoesNotExist:
            self.currently_expired_jobs = []

        return self.currently_expired_jobs

    def add_delayed_job_info(self, job, kwargs):
        last_beat_execution = datetime.utcnow() - timedelta(self.sleep_interval)
        last_beat_execution = last_beat_execution.replace(tzinfo=timezone('UTC'))

        if job.next_execution < last_beat_execution:
            kwargs[PeriodicJob.DELAYED_JOB] = True

        return kwargs

    def enqueue_next_jobs(self):
        for job in self.currently_expired_jobs:
            job_class, kwargs = self.get_class_and_kwargs(job)

            with transaction.atomic():
                curr_job = PeriodicJob.objects.select_for_update().get(
                    pk=job.id,
                    enabled=True,
                    next_execution__lte=datetime.utcnow()
                )
                logger.info('Queuing %s', job.name)
                curr_job.skip_delayed_jobs_this_time = self.skip_delayed_jobs
                kwargs = self.add_delayed_job_info(curr_job, kwargs)
                self.broker.add_job(job_class, **kwargs)
                curr_job.save()

    def run_forever(self):
        while True:
            while self.get_expired_jobs():
                self.enqueue_next_jobs()
            time.sleep(self.sleep_interval)
