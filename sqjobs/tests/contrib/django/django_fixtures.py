from sqjobs.contrib.django.djsqjobs.result_job import ResultJob
from sqjobs.contrib.django.djsqjobs.models import JobStatus

from ...fixtures import Divider


class ResultDivider(ResultJob):
    name = 'resultdivider'

    def __init__(self):
        super(ResultDivider, self).__init__()

    def pre_run(self, *args, **kwargs):
        super_setup = super(ResultDivider, self).pre_run(*args, **kwargs)
        return super_setup

    def run(self, num1, num2, *args, **kwargs):
        self.result = num1 // num2
        return self.result

    def on_failure(self, *args, **kwargs):
        super_on_failure = super(ResultDivider, self).on_failure(*args, **kwargs)
        self.err = 'ZeroDivisionError'
        return super_on_failure
