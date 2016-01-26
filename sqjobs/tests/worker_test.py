import pytest

from ..connectors.dummy import Dummy as DummyConnector
from ..worker import Worker
from ..brokers.standard import Standard as StandardBroker
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

    def test_try_register_abstract_job(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(AbstractAdder)

        assert len(worker.registered_jobs) == 0

    def test_register_same_job_twice(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)
        worker.register_job(Adder)

        assert len(worker.registered_jobs) == 1
        assert worker.registered_jobs[Adder.name] == Adder

    def test_overwrite_job_when_register_with_same_name(self):
        worker = Worker(self.broker, 'default')
        worker.register_job(Adder)
        worker.register_job(FakeAdder)

        assert len(worker.registered_jobs) == 1
        assert worker.registered_jobs[FakeAdder.name] == FakeAdder
