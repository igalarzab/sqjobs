from django.db import models
import pytz
from croniter.croniter import croniter
from datetime import datetime, timedelta


class JobStatus(models.Model):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    TIMEOUT = 'TIMEOUT'
    statuses = (
        (PENDING, 'PENDING'),
        (SUCCESS, 'SUCCESS'),
        (TIMEOUT, 'TIMEOUT'),
        (FAILURE, 'FAILURE')
    )

    # Job result/status
    job_id = models.TextField(
        "job id",
        unique=True
    )
    job_name = models.CharField(
        "job name",
        max_length=255,
        unique=False
    )
    status = models.CharField(
        "job status",
        max_length=7,
        default=PENDING,
        choices=statuses
    )
    result = models.TextField(
        null=True,
        default=None
    )
    date_started = models.DateTimeField(
        "started at",
        auto_now_add=True
    )
    date_done = models.DateTimeField(
        "done at",
        auto_now=False,
        null=True
    )
    traceback = models.TextField(
        "traceback",
        blank=True,
        null=True
    )

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "status": self.status,
            "result": self.result,
            "date_started": self.date_done,
            "date_done": self.date_done,
            "traceback": self.traceback
        }

    def __unicode__(self):
        return "<Job ({name}): {id} status->{status}>".format(
            name=self.job_name,
            id=self.job_id,
            status=self.status
        )


class PeriodicJob(models.Model):
    PROGRAMMED_DATE = 'sqjobs_programmed_date'
    DELAYED_JOB = 'sqjobs_delayed_job'

    name = models.CharField(
        "name",
        max_length=255,
        unique=False
    )
    task = models.CharField(
        "task",
        max_length=255,
        unique=False
    )
    args = models.TextField(
        "args",
        null=True,
        default=None
    )
    kwargs = models.TextField(
        "kwargs",
        null=True,
        default=None
    )
    schedule = models.CharField(
        "schedule",
        max_length=255,
        unique=False
    )
    timezone = models.CharField(
        "timezone",
        max_length=63,
        unique=False,
        default="UTC"
    )
    created_on = models.DateTimeField(
        "created on",
        auto_now_add=True
    )
    next_execution = models.DateTimeField(
        "next execution on",
        auto_now=False
    )
    enabled = models.BooleanField(
        "enabled",
        default=True
    )
    skip_delayed_jobs_next_time = models.BooleanField(
        "skip jobs if delayed",
        default=True
    )

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
