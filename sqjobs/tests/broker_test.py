import pytest

from ..connectors.dummy import Dummy
from ..brokers.broker import Standard
from ..brokers.eager import Eager
from .fixtures import Adder, Divider


class TestBroker(object):

    @property
    def connector(self):
        return Dummy()

    def test_broker_repr(self):
        broker = Standard(self.connector)
        assert repr(broker) == 'Broker(Dummy)'
        broker = Eager()
        assert repr(broker) == 'Broker(Eager)'

    def test_add_jobs_to_broker(self):
        broker = Standard(self.connector)
        broker.add_job(Adder, 2, 3)

        queues = list(broker.connector.jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_jobs == 1

        messages = broker.connector.jobs['default']
        assert len(messages) == 1

    def test_add_invalid_job(self):
        broker = Standard(self.connector)
        with pytest.raises(ValueError):
            broker.add_job(Dummy, 2, 3)

    def test_payload_args(self):
        broker = Standard(self.connector)
        broker.add_job(Adder, 2, 3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (2, 3), 'kwargs': {}, 'name': 'adder'}
        payload['job_id'] = message['job_id']
        assert message == payload

    def test_eager_execution(self):
        broker = Eager()
        assert broker.add_job(Adder, 2, 3)[1].result == 5

    def test_eager_failure(self):
        broker = Eager()
        assert broker.add_job(Divider, 2, 0)[1].err == "ZeroDivisionError"

    def test_payload_kwargs(self):
        broker = Standard(self.connector)
        broker.add_job(Adder, num2=2, num1=3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (), 'kwargs': {'num1': 3, 'num2': 2}, 'name': 'adder'}
        payload['job_id'] = message['job_id']
        assert message == payload

    def test_both_payloads(self):
        broker = Standard(self.connector)
        broker.add_job(Adder, 2, num2=3)

        message = broker.connector.jobs['default'][0]
        payload = {'args': (2,), 'kwargs': {'num2': 3}, 'name': 'adder'}
        payload['job_id'] = message['job_id']
        assert message == payload

    def test_read_job(self):
        job_ids = []
        broker = Standard(self.connector)
        job_ids.append(broker.add_job(Adder, 1, 1)[0])
        job_ids.append(broker.add_job(Adder, 2, 2)[0])

        gen = broker.jobs('default')
        jobs = []

        for _ in range(2):
            jobs.append(next(gen))

        assert len(jobs) == 2
        assert jobs[0] == {'job_id': job_ids[1], 'args': (2, 2), 'kwargs': {}, 'name': 'adder'}
        assert jobs[1] == {'job_id': job_ids[0], 'args': (1, 1), 'kwargs': {}, 'name': 'adder'}

    def test_read_empty_jobs_without_waiting(self):
        broker = Standard(self.connector)
        gen = broker.jobs('default', nowait=True)
        assert next(gen) is None

    def test_delete_job(self):
        broker = Standard(self.connector)
        adder = Adder()
        adder.queue = 'default'
        adder.broker_id = '123456789'

        broker.delete_job(adder)

        queues = list(broker.connector.deleted_jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_deleted_jobs == 1

        messages = broker.connector.deleted_jobs['default']
        assert len(messages) == 1
        assert messages[0] == '123456789'

    def test_retry_time_job(self):
        broker = Standard(self.connector)
        adder = Adder()
        adder.queue = 'default'
        adder.broker_id = '123456789'

        broker.set_retry_time(adder, 10)

        queues = list(broker.connector.retried_jobs.keys())
        assert len(queues) == 1
        assert queues[0] == 'default'
        assert broker.connector.num_retried_jobs == 1

        messages = broker.connector.retried_jobs['default']
        assert len(messages) == 1
        assert messages[0] == ('123456789', 10)

    def test_queues(self):
        broker = Standard(self.connector)

        queues = broker.queues()

        assert len(queues) == 0

        broker.add_job(Adder, 1, 2)

        queues = list(broker.queues())

        assert len(queues) == 1
        assert queues[0] == 'default'

    def test_dead_letter_queues(self):
        broker = Standard(self.connector)

        broker.add_job(Adder, 1, 2)

        queues = broker.dead_letter_queues()

        # Dummy connector defines no dead-letter queue
        assert len(queues) == 0
