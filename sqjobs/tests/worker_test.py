import pytest

from ..connectors.dummy import Dummy as DummyConnector
from ..worker import Worker
from ..brokers.broker import Standard as StandardBroker
from .fixtures import Adder, FakeAdder, AbstractAdder, RetryJob, ExceptionJob


class TestWorker(object):

    @property
    def connector(self):
        return DummyConnector()

    @property
    def broker(self):
        return StandardBroker(self.connector)

    def test_worker_repr(self):
        worker = Worker(self.broker, 'default')
        assert repr(worker) == 'Worker(Dummy)'

    def test_register_job(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)

        assert len(worker.registered_jobs) == 1
        assert worker.registered_jobs[Adder.name] == Adder

    def test_register_abstract_job(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(AbstractAdder)

        assert len(worker.registered_jobs) == 0

    def test_register_job_twice(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)
        worker.register_job(Adder)

        assert len(worker.registered_jobs) == 1
        assert worker.registered_jobs[Adder.name] == Adder

    def test_register_job_overwrite(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)
        worker.register_job(FakeAdder)

        assert len(worker.registered_jobs) == 1

    def test_job_builder(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)

        payload = self._job_payload(1, 'adder', 'default', 2, [1, 2])
        job, args, kwargs = worker._build_job(payload)

        assert isinstance(job, Adder)
        assert args == [1, 2]
        assert kwargs == {}
        assert job.id == 1
        assert job.queue == 'default'
        assert job.retries == 2

    def test_invalid_job_builder(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)

        payload = self._job_payload(1, 'WRONG', 'default', 2, [1, 2])

        with pytest.raises(ValueError):
            worker._build_job(payload)

    def test_change_retry_time(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)

        payload = self._job_payload(1, 'adder', 'default', 2, [1, 2])
        job, _, _ = worker._build_job(payload)

        worker._change_retry_time(job)

        assert len(worker.broker.connector.retried_jobs['default']) == 1
        assert worker.broker.connector.retried_jobs['default'][0] == (1, 10)

    def test_execute(self):
        connector = DummyConnector()
        payload = self._job_payload(1, 'adder', 'default', 0, [1, 3])
        connector.enqueue('default', payload)
        assert len(connector.get_queue('default')) == 1

        broker = StandardBroker(connector)

        worker = Worker(broker, 'default')
        worker.register_job(Adder)
        worker.execute(forever=False)

        assert len(connector.get_queue('default')) == 0
        assert len(connector.retried_jobs) == 0

    def test_execute_with_retry(self):
        connector = DummyConnector()
        payload = self._job_payload(1, 'retry', 'default')
        connector.enqueue('default', payload)
        assert len(connector.get_queue('default')) == 1

        broker = StandardBroker(connector)

        assert RetryJob.has_retried() is False
        worker = Worker(broker, 'default')
        worker.register_job(RetryJob)
        worker.execute(forever=False)

        assert len(connector.get_queue('default')) == 0
        assert len(connector.retried_jobs) == 1
        assert RetryJob.has_retried() is True

    def test_execute_with_exception(self):
        connector = DummyConnector()
        payload = self._job_payload(1, 'exception', 'default')
        connector.enqueue('default', payload)
        assert len(connector.get_queue('default')) == 1

        broker = StandardBroker(connector)

        assert ExceptionJob.has_failed() is False
        worker = Worker(broker, 'default')
        worker.register_job(ExceptionJob)
        worker.execute(forever=False)

        assert len(connector.get_queue('default')) == 0
        assert len(connector.retried_jobs) == 1
        assert ExceptionJob.has_failed() is True

    def _job_payload(self, jid, name, queue, retries=0, args=None, kwargs=None):
        return {
            'job_id': jid,
            'name': name,
            'queue': queue,
            'args': args or [],
            'kwargs': kwargs or {},
            '_metadata': {
                'id': jid,
                'retries': retries,
                'created_on': 'NOW',
                'first_execution_on': 'NOW',
            },
        }
