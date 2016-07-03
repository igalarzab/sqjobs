import pytest

from sqjobs import Job, RetryException
from .fixtures import Adder, Divider, ComplexRetryJob


class TestJobs(object):

    def test_job_class_defaults(self):
        assert Job.default_queue_name == 'sqjobs'
        assert Job.retry_time is None
        assert Job.name is None
        assert Job.abstract is False
        assert Job._task_name() == 'Job'

        with pytest.raises(TypeError):
            Job()

        with pytest.raises(NotImplementedError):
            Job.run(Adder())

    def test_job_obj_defaults(self):
        adder = Adder()

        assert repr(adder) == 'Adder()'
        assert adder.id is None
        assert adder.retries == 0
        assert adder.created_on is None
        assert adder.queue_name is None
        assert adder.broker_id is None
        assert hasattr(adder, 'result') is False

    def test_overwritten_default_queue(self):
        assert Divider().default_queue_name == 'math_operations'

    def test_job_names(self):
        adder = Adder()
        assert adder.name == 'adder'
        assert adder._task_name() == 'adder'

    def test_run_job_directly(self):
        adder = Adder()
        assert adder.run(1, 3) == 4

    def test_execute_job_directly(self):
        adder = Adder()
        adder.execute(1, 3)
        assert adder.result == 4

    def test_whole_execute_lifecycle_job(self):
        divider = Divider()
        divider.execute(2, 1)
        assert divider.result == '3'

    def test_retry_raises_exception(self):
        adder = Adder()

        with pytest.raises(RetryException):
            adder.retry()

    def test_simple_next_retry(self):
        adder = Adder()
        assert adder.next_retry_time() == 10


class TestRetries(object):

    def test_first_complex_retry(self):
        job = ComplexRetryJob()
        assert job.retry_time == 10
        assert job.next_retry_time() == 10

    def test_second_complex_retry(self):
        job = ComplexRetryJob()
        job.retries = 1

        assert job.next_retry_time() == 20
