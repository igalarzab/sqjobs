import json
from abc import abstractmethod, ABCMeta
from six import add_metaclass
from datetime import datetime

from sqjobs import Job
from sqjobs.contrib.django.djsqjobs.models import JobStatus

@add_metaclass(ABCMeta)
class ResultJob(Job):

    def prerun(self):
        self.job_status = JobStatus(
            job_id=self.id.split('#')[0],
            job_type=self.__repr__()
        )
        self.job_status.save()
        print self.job_status.job_id

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def postrun(self, finished_properly, result):
        self.job_status.date_done = datetime.now()
        self.job_status.result = json.dumps(result)
        if finished_properly:
            self.job_status.status = JobStatus.SUCCESS
        else:
            self.job_status.status = JobStatus.FAILURE
        self.job_status.save()

