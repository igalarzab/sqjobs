import json
from abc import abstractmethod, ABCMeta
from six import add_metaclass
from datetime import datetime

from sqjobs import Job
from sqjobs.contrib.django.djsqjobs.models import JobStatus

class DuplicatedTaskException(Exception):
    def __init__(self, message, errors=None):
        super(DuplicatedTaskException, self).__init__(message)
        self.errors = errors

@add_metaclass(ABCMeta)
class ResultJob(Job):

    def __init__(self):
        self.properly_setup = False

    def set_up(self, *args, **kwargs):
        super(ResultJob, self).set_up(*args, **kwargs)
        # Take as id the left part from the hash symbol
        task_id = self.id.split('#')[0]
        try:
            self.job_status = JobStatus(
                job_id=task_id,
                job_type=self.__repr__()
            )
            self.job_status.save(force_insert=True)
            self.properly_setup = True
        except:
            self.job_status = JobStatus.objects.get(job_id=task_id)
            if self.job_status.status == JobStatus.FAILURE:
                self.job_status.status = JobStatus.PENDING
                self.job_status.save()
                self.properly_setup = True
            else:
                raise DuplicatedTaskException('Task duplicated: %s' % task_id)

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def tear_down(self, *args, **kwargs):
        self.job_status.date_done = datetime.now()
        self.job_status.result = json.dumps(self.result)
        self.job_status.save(force_update=True)
        super(ResultJob, self).tear_down(*args, **kwargs)

    def on_success(self, *args, **kwargs):
        self.job_status.status = JobStatus.SUCCESS
        self.job_status.save(force_update=True)
        super(ResultJob, self).on_success(*args, **kwargs)

    def on_failure(self, *args, **kwargs):
        if self.properly_setup:
            self.job_status.status = JobStatus.FAILURE
            self.job_status.save(force_update=True)
        super(ResultJob, self).on_failure(*args, **kwargs)

