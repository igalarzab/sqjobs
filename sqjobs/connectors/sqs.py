from datetime import datetime
import json

import boto.sqs
import boto.sqs.message

import logging
logger = logging.getLogger('sqjobs.sqs')


class SQS(object):
    """
    Manages a single connection to SQS
    """

    def __init__(self, access_key, secret_key, region='us-east-1'):
        """
        Creates a new SQS object

        :param access_key: access key with access to SQS
        :param secret_key: secret key with access to SQS
        :param region: a valid region of AWS, like 'us-east-1'
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region

        self._cached_connection = None

    def __repr__(self):
        return 'SQS("{ak}", "{sk}", region="{region}")'.format(
            ak=self.access_key,
            sk=self.secret_key,
            region=self.region
        )

    @property
    def connection(self):
        """
        Creates (and saves in a cache) a SQS connection
        """
        if self._cached_connection is None:
            self._cached_connection = boto.sqs.connect_to_region(
                self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )

            logger.debug('Created new SQS connection')

        return self._cached_connection

    def create_queue(self, name):
        """
        Creates a new queue

        :param name: the name of the queue
        """
        self.connection.create_queue(name)
        logger.info('Created queue %s', name)

    def delete_queue(self, name):
        """
        Deletes a queue

        :param name: the name of the queue
        """
        self.connection.delete_queue(name)
        logger.info('Deleted queue %s', name)

    def get_queue(self, name):
        """
        Gets a queue given it name

        :param name: the name of the queue
        """
        queue = self.connection.get_queue(name)
        return queue

    def enqueue(self, queue_name, payload):
        """
        Sends a new message to a queue

        :param queue_name: the name of the queue
        :param payload: the payload to send inside the message
        """
        message = self._encode_message(payload)
        queue = self.get_queue(queue_name)

        if not queue:
            raise ValueError('The queue does not exist: %s' % queue_name)

        queue.write(message)
        logger.info('Sent new message to %s', queue_name)

    def dequeue(self, queue_name, visibility_timeout=None, wait_time=20):
        """
        Receive new messages from a queue

        :param queue_name: the queue name
        :param visibility_timeout: how much time to block the message
        until other workers can obtain access to it.
        :param wait_time: how much time to wait until a new message is
        retrieved (long polling). If set to zero, connection will return
        inmediately if no messages exist.
        """
        messages = None
        queue = self.get_queue(queue_name)

        if not queue:
            raise ValueError('The queue does not exist: %s' % queue_name)

        while not messages:
            messages = queue.get_messages(
                wait_time_seconds=wait_time,
                visibility_timeout=visibility_timeout,
                attributes='All',
            )

            if not messages and wait_time == 0:
                return None  # Non-blocking mode

            if not messages:
                logger.debug('No messages retrieved from %s', queue_name)

        logger.info('New message retrieved from %s', queue_name)
        payload = self._decode_message(messages[0])

        return payload

    def delete(self, queue_name, message_id):
        """
        Deletes a message from a queue

        :param queue_name: the name of the queue
        :param message_id: the message id
        """
        queue = self.get_queue(queue_name)

        if not queue:
            raise ValueError('The queue does not exist: %s' % queue_name)

        self.connection.delete_message_from_handle(queue, message_id)
        logger.info('Deleted message from queue %s', queue_name)

    def set_retry_time(self, queue_name, message_id, delay):
        """
        Changes the retry time of a message

        :param queue_name: the name of the queue
        :param message_id: the message id
        :param delay: delay (in seconds) of the next retry
        """
        queue = self.get_queue(queue_name)

        if not queue:
            raise ValueError('The queue does not exist: %s' % queue_name)

        self.connection.change_message_visibility(queue, message_id, delay)
        logger.info('Change retry time of a message from queue %s', queue_name)

    def _encode_message(self, payload):
        payload_str = json.dumps(payload)

        message = boto.sqs.message.Message()
        message.set_body(payload_str)

        return message

    def _decode_message(self, message):
        payload = json.loads(message.get_body())

        retries = int(message.attributes['ApproximateReceiveCount'])
        created_on = int(message.attributes['SentTimestamp'])
        first_execution_on = int(message.attributes['ApproximateFirstReceiveTimestamp'])

        payload['_metadata'] = {
            'id': message.receipt_handle,
            'retries': retries,
            'created_on': datetime.fromtimestamp(created_on / 1000),
            'first_execution_on': datetime.fromtimestamp(first_execution_on / 1000)
        }

        logging.debug('Message payload %s', str(payload))

        return payload
