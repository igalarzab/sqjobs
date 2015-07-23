import time
import sys
import json
from datetime import datetime, timedelta
import logging

from django.db import transaction

from .models import PeriodicJob

logger = logging.getLogger('sqjobs.beat')

class Beat(object):
    def __init__(self, broker, sleep_interval=10):
        self.broker = broker
        self.sleep_interval = sleep_interval
        self.currently_expired_jobs = []

    def get_class_and_kwargs(self, job):
        m_name, c_name = job.task.rsplit('.', 1)
        import importlib
        m = importlib.import_module(m_name)
        job_class = getattr(m, c_name)
        kwargs = json.loads(job.args)
        if 'programmed_date' not in kwargs:
            kwargs['programmed_date'] = job.next_execution.isoformat()
        return job_class, kwargs

    def get_expired_jobs(self):
        utc_now = datetime.utcnow()
        try:
            self.currently_expired_jobs = PeriodicJob.objects.filter(
                enabled=True,
                next_execution__lte=utc_now,
            )
        except PeriodicJob.DoesNotExist:
            self.currently_expired_jobs = []

        return self.currently_expired_jobs

    def enqueue_next_jobs(self):
        for job in self.currently_expired_jobs:
            job_class, kwargs = self.get_class_and_kwargs(job)

            utc_now = datetime.utcnow()
            utc_before = utc_now - timedelta(seconds=self.sleep_interval)

            with transaction.atomic():
                curr_job = PeriodicJob.objects.select_for_update().get(
                    pk=job.id,
                    enabled=True,
                    next_execution__lte=utc_now
                )
                logger.info('Queuing %s', job.name)
                self.broker.add_job(job_class, **kwargs)
                curr_job.save()

    def run_forever(self):
        while True:
            while self.get_expired_jobs():
                self.enqueue_next_jobs()
            time.sleep(self.sleep_interval)
