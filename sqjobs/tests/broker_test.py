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
