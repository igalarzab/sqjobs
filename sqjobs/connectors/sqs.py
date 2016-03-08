from datetime import date, datetime
import base64
import json

import boto3
import botocore

from .base import Connector
from ..exceptions import QueueDoesNotExist

import logging
logger = logging.getLogger('sqjobs.sqs')


class SQS(Connector):
    """
    Manages a single connection to SQS
    """

    def __init__(self, access_key, secret_key, region_name='us-east-1', endpoint_url=None):
        """
        Creates a new SQS object

        :param access_key: access key with write access to AWS SQS
        :param secret_key: secret key with write access to AWS SQS
        :param region_name: a region name, like 'us-east-1'
        :param endpoint_url: URL to use a custom region
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url

        self._cached_connection = None

    def __repr__(self):
        return 'SQS("{ak}", "{sk}", region_name="{region_name}")'.format(
            ak=self.access_key,
            sk="%s******%s" % (self.secret_key[0:6], self.secret_key[-4:]),
            region_name=self.region_name,
        )

    @property
    def connection(self):
        """
        Creates (and saves in a cache) a connection to SQS
        """
        if self._cached_connection is None:
            config = {
                'service_name': 'sqs',
                'region_name': self.region_name,
                'aws_access_key_id': self.access_key,
                'aws_secret_access_key': self.secret_key,
            }

            if self.endpoint_url:
                config['endpoint_url'] = self.endpoint_url

            self._cached_connection = boto3.resource(**config)
            logger.debug('Created a new connection to SQS')

        return self._cached_connection

    def enqueue(self, queue_name, payload):
        message = self._encode_message(payload)
        queue = self._get_queue(queue_name)

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        queue.send_message(MessageBody=message)
        logger.info('Sent new message to %s', queue_name)

    def dequeue(self, queue_name, wait_time=20):
        queue = self._get_queue(queue_name)
        messages = None

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        while not messages:
            messages = queue.receive_messages(
                MaxNumberOfMessages=1,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All'],
            )

            if not messages:
                logger.debug('No message retrieved from %s', queue_name)

                if wait_time == 0:
                    return None  # Non-blocking mode

        logger.info('New message retrieved from %s', queue_name)
        payload = self._decode_message(messages[0])

        return payload

    def delete(self, queue_name, message_id):
        queue = self._get_queue(queue_name)

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        queue.delete_messages(Entries=[{
            'Id': '1',
            'ReceiptHandle': message_id
        }])

        logger.info('Deleted message from queue %s', queue_name)

    def retry(self, queue_name, message_id, delay):
        queue = self._get_queue(queue_name)

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        queue.change_message_visibility_batch(Entries=[{
            'Id': '1',
            'ReceiptHandle': message_id,
            'VisibilityTimeout': delay or 0
        }])

        logger.info('Changed retry time of a message from queue %s', queue_name)

    def serialize_job(self, job_class, job_id, args, kwargs):
        return {
            'id': job_id,
            'name': job_class._task_name(),
            'args': args,
            'kwargs': kwargs
        }

    def unserialize_job(self, job_class, queue_name, payload):
        job = job_class()

        job.id = payload['id']
        job.queue_name = queue_name
        job.broker_id = payload['_metadata']['id']
        job.retries = payload['_metadata']['retries']
        job.created_on = payload['_metadata']['created_on']
        args = payload['args'] or []
        kwargs = payload['kwargs'] or {}

        return job, args, kwargs

    def _get_queue(self, name):
        try:
            return self.connection.get_queue_by_name(QueueName=name)
        except botocore.exceptions.ClientError:
            return None

    def _encode_message(self, payload):
        payload_str = json.dumps(payload, default=self._json_formatter)
        payload_encoded = base64.b64encode(payload_str)
        return payload_encoded

    def _decode_message(self, message):
        payload_decoded = base64.b64decode(message.body)
        payload = json.loads(payload_decoded)

        retries = int(message.attributes['ApproximateReceiveCount'])
        created_on = int(message.attributes['SentTimestamp'])

        payload['_metadata'] = {
            'id': message.receipt_handle,
            'retries': retries,
            'created_on': datetime.fromtimestamp(created_on / 1000),
        }

        logging.debug('Message payload: %s', str(payload))

        return payload

    def _json_formatter(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')

        return None
