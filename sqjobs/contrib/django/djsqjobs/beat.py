import json
import time
from datetime import datetime, timedelta
from pytz import timezone

from django.db import transaction

from .models import PeriodicJob

import logging
logger = logging.getLogger('sqjobs.contrib.django.beat')


class Beat(object):
    """
    A cron-like worker that execute scheduled jobs
    """

    def __init__(self, broker, sleep_interval=10, skip_delayed_jobs=True):
        self.broker = broker
        self.sleep_interval = sleep_interval
        self.skip_delayed_jobs = skip_delayed_jobs
        self.registered_jobs = {}

    def register_job(self, job_class):
        name = job_class._task_name()

        if name in self.registered_jobs:
            logger.warning('Job %s already registered', name)

        if job_class.abstract:
            return

        self.registered_jobs[name] = job_class

    def get_job_kwargs(self, job):
        job_kwargs = json.loads(job.kwargs)
        job_kwargs[PeriodicJob.PROGRAMMED_DATE] = job.next_execution.astimezone(timezone(job.timezone)).isoformat()
        return job_kwargs

    def get_job_args(self, job):
        if job.args:
            return tuple(json.loads(job.args))
        return []

    def get_expired_jobs(self):
        return PeriodicJob.objects.filter(
            enabled=True,
            next_execution__lte=datetime.utcnow(),
        )

    def add_delayed_job_info(self, job, job_kwargs):
        last_beat_execution = datetime.utcnow() - timedelta(seconds=self.sleep_interval)
        last_beat_execution = last_beat_execution.replace(tzinfo=timezone('UTC'))

        if job.next_execution < last_beat_execution:
            job_kwargs[PeriodicJob.DELAYED_JOB] = True

        return job_kwargs

    def enqueue_next_jobs(self, currently_expired_jobs):
        for job in currently_expired_jobs:
            job_class = self.registered_jobs[job.task]
            job_args = self.get_job_args(job)
            job_kwargs = self.get_job_kwargs(job)

            with transaction.atomic():
                curr_job = PeriodicJob.objects.select_for_update().get(
                    pk=job.id,
                    enabled=True,
                    next_execution__lte=datetime.utcnow()
                )
                logger.info('Queuing %s', job.name)
                curr_job.skip_delayed_jobs_next_time = self.skip_delayed_jobs
                curr_job.save()
                job_kwargs = self.add_delayed_job_info(curr_job, job_kwargs)
                self.broker.add_job(job_class, *job_args, **job_kwargs)

    def run_forever(self):
        while True:
            self.enqueue_next_jobs(self.get_expired_jobs())
            time.sleep(self.sleep_interval)
