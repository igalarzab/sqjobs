from .job import Job
from .metadata import __version__, __license__


def create_sqs_broker(access_key, secret_key, region='us-west-1', is_secure=True):
    from .connectors.sqs import SQS
    from .broker import Broker

    sqs = SQS(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        is_secure=is_secure
    )

    broker = Broker(sqs)
    return broker


def create_sqs_worker(queue_name, access_key, secret_key, region='us-west-1', is_secure=True):
    from .worker import Worker

    broker = create_sqs_broker(access_key, secret_key, region, is_secure)
    worker = Worker(broker, queue_name)

    return worker
