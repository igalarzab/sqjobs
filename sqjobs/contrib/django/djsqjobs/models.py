import pytz
from datetime import datetime, timedelta

from croniter.croniter import croniter
from django.db import models
from django.utils.translation import ugettext_lazy as _


class JobStatus(models.Model):
    """
    Stores in the database the status of a job execution
    """
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

    statuses = (
        (PENDING, 'PENDING'),
        (SUCCESS, 'SUCCESS'),
        (FAILURE, 'FAILURE')
    )

    job_id = models.CharField(_('job id'), max_length=255, unique=True)
    job_name = models.CharField(_('job name'), max_length=255)
    status = models.CharField(_('status'), max_length=7, default=PENDING, choices=statuses)
    result = models.TextField(_('result'), blank=True)
    traceback = models.TextField(_('traceback'), blank=True)

    created_at = models.DateTimeField(_('started at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('done at'), auto_now=True)

    def __repr__(self):
        return '<JobStatus ({name}): {id} status->{status}>'.format(
            name=self.job_name,
            id=self.job_id,
            status=self.status
        )


class PeriodicJob(models.Model):
    """
    A scheduled job
    """
    PROGRAMMED_DATE = 'sqjobs_programmed_date'
    DELAYED_JOB = 'sqjobs_delayed_job'

    name = models.CharField(_('name'), max_length=255)
    task = models.CharField(_('task'), max_length=255)
    args = models.TextField(_('args'), blank=True)
    kwargs = models.TextField(_('kwargs'), blank=True)

    schedule = models.CharField(_('schedule'), max_length=255)
    timezone = models.CharField(_('timezone'), max_length=63, default='UTC')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    next_execution = models.DateTimeField(_('next execution on'))

    enabled = models.BooleanField(_('enabled'), default=True)
    skip_delayed_jobs_next_time = models.BooleanField(_('skip jobs if delayed'), default=True)

    def save(self, *args, **kwargs):
        self.next_execution = self.get_next_utc_execution()
        super(PeriodicJob, self).save(*args, **kwargs)

    def get_next_utc_execution(self):
        tz = pytz.timezone(self.timezone)

        if not self.next_execution:
            base = tz.normalize(datetime.now(tz) - timedelta(minutes=1))
        elif self.skip_delayed_jobs_next_time:
            base = tz.normalize(datetime.now(tz))
        else:
            base = tz.normalize(self.next_execution.replace(tzinfo=pytz.utc))

        cron = croniter(self.schedule, base)

        return cron.get_next(datetime).astimezone(pytz.utc)
