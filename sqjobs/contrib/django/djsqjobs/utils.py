from django.conf import settings

from sqjobs import create_sqs_broker, create_sqs_worker


def get_broker():
    return create_sqs_broker(
        access_key=settings.SQJOBS_SQS_ACCESS_KEY,
        secret_key=settings.SQJOBS_SQS_SECRET_KEY,
        region_name=settings.SQJOBS_SQS_REGION_NAME,
        endpoint_url=getattr(settings, 'SQJOBS_SQS_ENDPOINT_URL', None),
    )


def get_worker(queue_name):
    return create_sqs_worker(
        queue_name=queue_name,
        access_key=settings.SQJOBS_SQS_ACCESS_KEY,
        secret_key=settings.SQJOBS_SQS_SECRET_KEY,
        region_name=settings.SQJOBS_SQS_REGION_NAME,
        endpoint_url=getattr(settings, 'SQJOBS_SQS_ENDPOINT_URL', None),
    )


def add_job(job_class, *args, **kwargs):
    get_broker().add_job(job_class, *args, **kwargs)
