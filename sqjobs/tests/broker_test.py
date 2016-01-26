import pytest

from .fixtures import Adder, Divider
from ..brokers.standard import Standard as StandardBroker
from ..brokers.eager import Eager as EagerBroker
from ..brokers.base import Broker as BaseBroker
from ..connectors.dummy import Dummy as DummyConnector


class TestBrokerInterface(object):

    def test_default_broker_interface(self):
        with pytest.raises(NotImplementedError):
            BaseBroker.add_job(StandardBroker(None), Adder, 'demo', {})


class TestStandardBroker(object):

    @property
    def connector(self):
        return DummyConnector()

    def test_broker_repr(self):
        broker = StandardBroker(self.connector)
        assert repr(broker) == 'Broker(Dummy)'

    def test_add_job_to_broker(self):
        broker = StandardBroker(self.connector)
        broker.add_job(Adder, 2, 3)

        queues = list(broker.connector.jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'sqjobs'
        assert broker.connector.num_jobs == 1

        messages = broker.connector.jobs['sqjobs']
        assert len(messages) == 1

    def test_right_payload_args_when_job_is_added(self):
        broker = StandardBroker(self.connector)
        broker.add_job(Adder, 2, 3)

        message = broker.connector.jobs['sqjobs'][0]
        del message['id']  # Check that exists, but we don't care about the value

        assert message == {'args': (2, 3), 'kwargs': {}, 'name': 'adder'}

    def test_right_payload_kwargs_when_job_is_added(self):
        broker = StandardBroker(self.connector)
        broker.add_job(Adder, num2=2, num1=3)

        message = broker.connector.jobs['sqjobs'][0]
        del message['id']  # Check that exists, but we don't care about the value

        assert message == {'args': (), 'kwargs': {'num1': 3, 'num2': 2}, 'name': 'adder'}

    def test_right_payload_both_when_job_is_added(self):
        broker = StandardBroker(self.connector)
        broker.add_job(Adder, 2, num2=3)

        message = broker.connector.jobs['sqjobs'][0]
        del message['id']  # Check that exists, but we don't care about the value

        assert message == {'args': (2,), 'kwargs': {'num2': 3}, 'name': 'adder'}

    def test_multiple_jobs_are_stored_correctly_by_the_broker(self):
        broker = StandardBroker(self.connector)
        job_ids, jobs = [], []

        job_ids.append(broker.add_job(Adder, 1, 1))
        job_ids.append(broker.add_job(Adder, 2, 2))

        gen = broker.jobs('sqjobs')

        for _ in range(2):
            jobs.append(next(gen))

        assert len(jobs) == 2
        assert jobs[0] == {'id': job_ids[1].job_id, 'args': (2, 2), 'kwargs': {}, 'name': 'adder'}
        assert jobs[1] == {'id': job_ids[0].job_id, 'args': (1, 1), 'kwargs': {}, 'name': 'adder'}


class TestEagerBroker(object):

    def test_broker_repr(self):
        broker = EagerBroker()
        assert repr(broker) == 'Broker(Eager)'

    def test_execute_job_eager_mode(self):
        broker = EagerBroker()
        result = broker.add_job(Adder, 2, 3)
        assert result.result == 5

    def test_eager_failure(self):
        broker = EagerBroker()

        with pytest.raises(ZeroDivisionError):
            assert broker.add_job(Divider, 2, 0)[1].err == "ZeroDivisionError"
