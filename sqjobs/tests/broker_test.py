import pytest

from ..connectors.dummy import Dummy
from ..broker import Broker
from .fixtures import Adder


class TestBroker(object):

    @property
    def connector(self):
        return Dummy()

    def test_broker_repr(self):
        broker = Broker(self.connector)
        assert repr(broker) == 'Broker(Dummy)'

    def test_add_jobs_to_broker(self):
        broker = Broker(self.connector)
        broker.add_job(Adder, 2, 3)

        queues = list(broker.connector.jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_jobs == 1

        messages = broker.connector.jobs['default']
        assert len(messages) == 1

    def test_add_invalid_job(self):
        broker = Broker(self.connector)
        with pytest.raises(ValueError):
            broker.add_job(Dummy, 2, 3)

    def test_payload_args(self):
        broker = Broker(self.connector)
        broker.add_job(Adder, 2, 3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (2, 3), 'kwargs': {}, 'name': 'adder'}
        assert message == payload

    def test_payload_kwargs(self):
        broker = Broker(self.connector)
        broker.add_job(Adder, num2=2, num1=3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (), 'kwargs': {'num1': 3, 'num2': 2}, 'name': 'adder'}
        assert message == payload

    def test_both_payloads(self):
        broker = Broker(self.connector)
        broker.add_job(Adder, 2, num2=3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (2,), 'kwargs': {'num2': 3}, 'name': 'adder'}
        assert message == payload

    def test_read_job(self):
        broker = Broker(self.connector)
        broker.add_job(Adder, 1, 1)
        broker.add_job(Adder, 2, 2)

        gen = broker.jobs('default')
        jobs = []

        for _ in range(2):
            jobs.append(gen.next())

        assert len(jobs) == 2
        assert jobs[0] == {'args': (2, 2), 'kwargs': {}, 'name': 'adder'}
        assert jobs[1] == {'args': (1, 1), 'kwargs': {}, 'name': 'adder'}

    def test_delete_job(self):
        broker = Broker(self.connector)
        adder = Adder()
        adder.queue = 'default'
        adder.id = '123456789'

        broker.delete_job(adder)

        queues = list(broker.connector.deleted_jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_deleted_jobs == 1

        messages = broker.connector.deleted_jobs['default']
        assert len(messages) == 1
        assert messages[0] == '123456789'

    def test_retry_time_job(self):
        broker = Broker(self.connector)
        adder = Adder()
        adder.queue = 'default'
        adder.id = '123456789'

        broker.set_retry_time(adder, 10)

        queues = list(broker.connector.retried_jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_retried_jobs == 1

        messages = broker.connector.retried_jobs['default']
        assert len(messages) == 1
        assert messages[0] == ('123456789', 10)
