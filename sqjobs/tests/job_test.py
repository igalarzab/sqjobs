import pytest

from ..job import Job, RetryException
from .fixtures import Adder, Divider, ComplexRetryJob


class TestJobDefaults(object):

    def test_default_queue_name(self):
        assert Job.default_queue_name == 'sqjobs'

    def test_no_default_retry_time(self):
        assert Job.retry_time is None

    def test_no_default_name(self):
        assert Job.name is None

    def test_default_name_generator(self):
        assert Job._task_name() == 'sqjobs.job|Job'

    def test_is_abstract_class(self):
        with pytest.raises(TypeError):
            Job()

    def test_run_is_not_implemented(self):
        adder = Adder()

        with pytest.raises(NotImplementedError):
            Job.run(adder)


class TestJobExample(object):

    def test_job_defaults(self):
        adder = Adder()
        assert repr(adder) == 'Adder()'
        assert adder.id is None
        assert adder.retries == 0
        assert adder.created_on is None

    def test_overwritten_default_queue(self):
        adder = Adder()
        assert adder.default_queue_name == 'sqjobs'

    def test_run_job_directly(self):
        adder = Adder()
        assert adder.run(1, 3) == 4

    def test_execute_job_directly(self):
        adder = Adder()
        adder.execute(1, 3)
        assert adder.result == 4

    def test_whole_execute_job(self):
        divider = Divider()
        divider.execute(2, 1)
        assert divider.result == '3'

    def test_job_names(self):
        adder = Adder()
        assert adder.name == 'adder'
        assert adder._task_name() == 'adder'

    def test_simple_next_retry(self):
        adder = Adder()
        assert adder.next_retry_time() == 10


class TestComplexRetries(object):

    def test_first_complex_retry(self):
        job = ComplexRetryJob()
        assert job.retry_time == 10
        assert job.next_retry_time() == 10

    def test_second_complex_retry(self):
        job = ComplexRetryJob()
        job.retries = 1

        assert job.next_retry_time() == 20
