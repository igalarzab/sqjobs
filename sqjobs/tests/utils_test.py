from sqjobs import metadata
from sqjobs.brokers.eager import Eager
from sqjobs.brokers.standard import Standard
from sqjobs.brokers.multiqueue import MultiQueue
from sqjobs.connectors.sqs import SQS
from sqjobs.utils import (
    create_sqs_broker, create_sqs_worker, get_jobs_from_module,
    create_eager_broker, create_multiqueue_sqs_worker
)
from sqjobs.worker import Worker
from .fixtures import Adder, AbstractAdder


class TestBuilders(object):

    def test_eager_broker_builder(self):
        broker = create_eager_broker()
        assert isinstance(broker, Eager)

    def test_broker_builder(self):
        broker = create_sqs_broker('access', 'secret')

        assert isinstance(broker, Standard)
        assert isinstance(broker.connector, SQS)

        assert broker.connector.access_key == 'access'
        assert broker.connector.secret_key == 'secret'
        assert broker.connector.region_name == 'us-west-1'

    def test_broker_builder_with_custom_zone(self):
        broker = create_sqs_broker('access', 'secret', 'eu-west-1')
        assert broker.connector.region_name == 'eu-west-1'

    def test_worker_builder(self):
        worker = create_sqs_worker('queue_name', 'access', 'secret')

        assert isinstance(worker, Worker)
        assert isinstance(worker.broker, Standard)
        assert isinstance(worker.broker.connector, SQS)

        assert worker.queue_name == 'queue_name'
        assert worker.broker.connector.access_key == 'access'
        assert worker.broker.connector.secret_key == 'secret'
        assert worker.broker.connector.region_name == 'us-west-1'

    def test_multiqueue_worker_builder(self):
        worker = create_multiqueue_sqs_worker(['queue_name'], 'access', 'secret')

        assert isinstance(worker, Worker)
        assert isinstance(worker.broker, MultiQueue)
        assert isinstance(worker.broker.connector, SQS)

        assert worker.queue_name == ['queue_name']
        assert worker.broker.connector.access_key == 'access'
        assert worker.broker.connector.secret_key == 'secret'
        assert worker.broker.connector.region_name == 'us-west-1'

    def test_jobs_extracter(self):
        jobs = get_jobs_from_module('sqjobs.tests.fixtures')

        assert len(jobs) is 6
        assert Adder in jobs
        assert AbstractAdder not in jobs

    def test_invalid_module(self):
        jobs = get_jobs_from_module('invalid.module')
        assert jobs == []

    def test_min_metadata_info(self):
        assert metadata.__uname__ is not None
        assert metadata.__version__ is not None
        assert metadata.__license__ is not None
