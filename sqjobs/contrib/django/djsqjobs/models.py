from django.db import models

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
    job_type = models.CharField(u"job type", max_length=255, unique=False)
    status = models.CharField(u"job status", max_length=7,
            default=PENDING, choices=states)
    result = models.TextField(null=True, default=None)
    date_started = models.DateTimeField(u"started at", auto_now_add=True)
    date_done = models.DateTimeField(u"done at", auto_now=False, null=True)
    traceback = models.TextField(u"traceback", blank=True, null=True)

    class Meta:
        """Model meta-data."""
        db_table = "sqjobs_jobstatus"

    def to_dict(self):
        return {"job_id": self.job_id,
                "job_type": self.job_type,
                "status": self.status,
                "result": self.result,
                "date_started": self.date_done,
                "date_done": self.date_done,
                "traceback": self.traceback}

    def __unicode__(self):
        return u"<Job: %s state->%s>" % (self.job_id, self.status)
