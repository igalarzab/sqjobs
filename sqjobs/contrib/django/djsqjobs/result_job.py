import json
from abc import abstractmethod, ABCMeta
from six import add_metaclass
from datetime import datetime
from functools import wraps

from sqjobs import Job
from sqjobs.contrib.django.djsqjobs.models import JobStatus

def backed_job(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.save_prerun()
        success, result = f(self, *args, **kwargs)
        self.save_postrun(success, result)
    return wrapper

@add_metaclass(ABCMeta)
class ResultJob(Job):

    def save_prerun(self):
        self.job_status = JobStatus(
            job_id=self.id.split('#')[0],
            job_type=self.__repr__()
        )
        self.job_status.save()

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def save_postrun(self, finished_properly, result):
        self.job_status.date_done = datetime.now()
        self.job_status.result = json.dumps(result)
        if finished_properly:
            self.job_status.status = JobStatus.SUCCESS
        else:
            self.job_status.status = JobStatus.FAILURE
        self.job_status.save()

