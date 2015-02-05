from .job import Job


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


__uname__ = 'sqjobs'
__long_name__ = 'Simple Queue Jobs'
__version__ = '0.5'
__author__ = 'Jose Ignacio Galarza'
__email__ = 'igalarzab@gmail.com'
__url__ = 'http://github.com/igalarzab/sqjobs'
__license__ = 'BSD'
