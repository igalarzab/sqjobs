from ..brokers.standard import Standard
from ..utils import create_sqs_broker, create_sqs_worker
from ..worker import Worker
from ..connectors.sqs import SQS


class TestBuilders(object):

    def test_broker_builder(self):
        broker = create_sqs_broker('access', 'secret')

        assert isinstance(broker, Standard)
        assert isinstance(broker.connector, SQS)

        assert broker.connector.access_key == 'access'
        assert broker.connector.secret_key == 'secret'
        assert broker.connector.region_name == 'us-west-1'

    def test_worker_builder(self):
        worker = create_sqs_worker('queue_name', 'access', 'secret')

        assert isinstance(worker, Worker)
        assert isinstance(worker.broker, Standard)
        assert isinstance(worker.broker.connector, SQS)

        assert worker.queue_name == 'queue_name'
        assert worker.broker.connector.access_key == 'access'
        assert worker.broker.connector.secret_key == 'secret'
        assert worker.broker.connector.region_name == 'us-west-1'
