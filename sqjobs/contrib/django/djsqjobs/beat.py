import time
import sys
import json
import pytz
from datetime import datetime, timedelta
import logging

from django.db import transaction

from .models import PeriodicJob

logger = logging.getLogger('sqjobs.beat')

class Beat(object):
    def __init__(self, broker, sleep_interval=10):
        self.broker = broker
        self.sleep_interval = sleep_interval

    def get_next_jobs(self):
        sleep_timedelta = timedelta(seconds=self.sleep_interval)
        utc_now = datetime.utcnow()
        utc_before = utc_now - sleep_timedelta

        try:
            jobs_to_execute = PeriodicJob.objects.filter(
                enabled=True,
                next_execution__lte=utc_now,
                next_execution__gt=utc_before
            )
        except PeriodicJob.DoesNotExist:
            return []

        return jobs_to_execute

    def get_class_and_kwargs(self, job):
        m_name, c_name = job.task.rsplit('.', 1)
        import importlib
        m = importlib.import_module(m_name)
        job_class = getattr(m, c_name)
        kwargs = json.loads(job.args)
        return job_class, kwargs

    def enqueue_next_jobs(self):
        for job in self.get_next_jobs():
            logger.info('Queuing %s', job.name)
            job_class, kwargs = self.get_class_and_kwargs(job)
            utc_now = datetime.utcnow()

            with transaction.atomic():
                curr_job = PeriodicJob.objects.select_for_update().get(
                    pk=job.id,
                    enabled=True,
                    next_execution__lte=utc_now
                )
                curr_job.save()
                self.broker.add_job(job_class, **kwargs)

    def run_forever(self):
        while True:
            self.enqueue_next_jobs()
            time.sleep(self.sleep_interval)
