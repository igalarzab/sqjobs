import base64
import json
import sys
from datetime import date, datetime
from kombu import Connection
from kombu.pools import producers
from pytz import timezone

from .base import Connector
from ..exceptions import QueueDoesNotExist

import logging
logger = logging.getLogger('sqjobs.rabbitmq')


class RabbitMQ(Connector):
    """
    Manages a single connection to RabbitMQ
    """

    def __init__(self, transport='amqp', endpoint_url='guest:guest@localhost:5672', exchange=None, queues={}):
        """
        Creates a new SQS object

        :param transport: amqp, librabbitmq, redis...
        :param endpoint_url: URL for the connection
        """
        self.transport = transport
        self.endpoint_url = endpoint_url
        self.exchange = exchange
        self.queues = queues

        self._cached_connection = None

    def __repr__(self):
        return 'RabbitMQ("{transport}://{url}//")'.format(
            transport=self.transport,
            url=self.endpoint_url,
        )

    @property
    def connection(self):
        """
        Creates (and saves in a cache) a connection to RabbitMQ
        """
        if self._cached_connection is None:
            self._cached_connection = Connection('{transport}://{url}//'.format(
                transport=self.transport,
                url=self.endpoint_url,
            ))
            logger.debug('Created a new connection to RabbitMQ')

        return self._cached_connection

    def enqueue(self, queue_name, payload):
        message = RabbitMQMessage.encode(payload)
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(
                payload,
                serializer='json',
                compression='bzip2',
                exchange=self.exchange,
                declare=[self.exchange],
                routing_key=priority,
            )
        logger.info('Sent new message to %s', queue_name)

    def dequeue(self, queue_name, wait_time=20):
        queue = self.queues.get(queue_name)
        message = None

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        while not message:
            message = queue.get()

            if not message:
                logger.debug('No message retrieved from %s', queue_name)

        logger.info('New message retrieved from %s', queue_name)
        payload = RabbitMQMessage.decode(message)

        return payload

    def delete(self, queue_name, message_id):
        queue = self.queues.get(queue_name)

        if not queue:
            raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

        queue.purge()

        logger.info('Deleted message from queue %s', queue_name)

    # def set_retry_time(self, queue_name, message_id, delay):
    #     queue = self.queues.get(queue_name)

    #     if not queue:
    #         raise QueueDoesNotExist('The queue %s does not exist' % queue_name)

    #     queue.change_message_visibility_batch(Entries=[{
    #         'Id': '1',
    #         'ReceiptHandle': message_id,
    #         'VisibilityTimeout': delay or 0
    #     }])

    #     logger.info('Changed retry time of a message from queue %s', queue_name)

    def serialize_job(self, job_name, job_id, args, kwargs):
        return {
            'id': job_id,
            'name': job_name,
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


class RabbitMQMessage(object):

    @staticmethod
    def encode(payload):
        payload_str = json.dumps(payload, default=RabbitMQMessage.json_formatter)
        payload_encoded = base64.b64encode(payload_str.encode('utf-8'))
        return payload_encoded.decode('utf-8')

    @staticmethod
    def decode(message):
        body = message.body

        payload_decoded = base64.b64decode(body)
        payload = json.loads(payload_decoded.decode("utf-8"))

        # retries = int(message.attributes['ApproximateReceiveCount'])
        # created_on = int(message.attributes['SentTimestamp'])

        # payload['_metadata'] = {
        #     'id': message.receipt_handle,
        #     'retries': retries,
        #     'created_on': datetime.fromtimestamp(created_on / 1000, tz=timezone('UTC')),
        # }

        logging.debug('Message payload: %s', str(payload))

        return payload

    @staticmethod
    def json_formatter(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')

        return None
