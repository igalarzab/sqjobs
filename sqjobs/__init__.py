def create_sqs_broker(access_key, secret_key, region='us-west-1'):
    from .connectors.sqs import SQS
    from .broker import Broker

    sqs = SQS(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
    )

    return Broker(sqs)


def create_sqs_worker(queue_name, access_key, secret_key, region='us-west-1'):
    from .worker import Worker

    broker = create_sqs_broker(access_key, secret_key, region)
    worker = Worker(broker, queue_name)

    return worker
