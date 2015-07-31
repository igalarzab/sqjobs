from django.db import models
import pytz


class JobStatus(models.Model):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    TIMEOUT = 'TIMEOUT'
    states = (
        (PENDING, 'PENDING'),
        (SUCCESS, 'SUCCESS'),
        (TIMEOUT, 'TIMEOUT'),
        (FAILURE, 'FAILURE')
    )

    """Job result/status."""
    job_id = models.CharField(u"job id", max_length=255, unique=True)
    job_name = models.CharField(u"job name", max_length=255, unique=False)
    status = models.CharField(
        u"job status", max_length=7, default=PENDING, choices=states
    )
    result = models.TextField(null=True, default=None)
    date_started = models.DateTimeField(u"started at", auto_now_add=True)
    date_done = models.DateTimeField(u"done at", auto_now=False, null=True)
    traceback = models.TextField(u"traceback", blank=True, null=True)

    def to_dict(self):
        return {"job_id": self.job_id,
                "job_name": self.job_name,
                "status": self.status,
                "result": self.result,
                "date_started": self.date_done,
                "date_done": self.date_done,
                "traceback": self.traceback}

    def __unicode__(self):
        return u"<Job (%s): %s state->%s>" % (self.job_name, self.job_id, self.status)


class PeriodicJob(models.Model):
    PROGRAMMED_DATE = 'sqjobs_programmed_date'
    DELAYED_JOB = 'sqjobs_delayed_job'

    name = models.CharField(u"name", max_length=255, unique=False)
    task = models.CharField(u"task", max_length=255, unique=False)
    args = models.TextField(u"args", null=True, default=None)
    kwargs = models.TextField(u"kwargs", null=True, default=None)
    schedule = models.CharField(u"schedule", max_length=255, unique=False)
    timezone = models.CharField(u"timezone", max_length=63, unique=False, default="UTC")
    created_on = models.DateTimeField(u"created on", auto_now_add=True)
    next_execution = models.DateTimeField(u"next execution on", auto_now=False)
    enabled = models.BooleanField(u"enabled", default=True)
    skip_delayed_jobs_next_time = models.BooleanField(u"skip jobs if delayed", default=True)

    def save(self, *args, **kwargs):
        self.next_execution = self.get_next_utc_execution()
        super(PeriodicJob, self).save(*args, **kwargs)

    def get_next_utc_execution(self):
        from croniter.croniter import croniter
        from datetime import datetime, timedelta
        tz = pytz.timezone(self.timezone)
        utc = pytz.timezone('UTC')

        if not self.next_execution:
            base = datetime.now(tz) - timedelta(minutes=1)

        elif self.skip_delayed_jobs_next_time:
            base = datetime.now(tz)
        else:
            base = self.next_execution

        ct = croniter(self.schedule, base)
        return ct.get_next(datetime).astimezone(utc)
