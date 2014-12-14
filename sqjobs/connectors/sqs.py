from datetime import datetime
import json

import boto.sqs
import boto.sqs.message


class SQS(object):

    def __init__(self, access_key, secret_key, region='us-east-1'):
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
        if self._cached_connection is None:
            self._cached_connection = boto.sqs.connect_to_region(
                self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )

        return self._cached_connection

    def create_queue(self, name):
        self.connection.create_queue(name)

    def delete_queue(self, name):
        self.connection.delete_queue(name)

    def get_queue(self, queue_name):
        queue = self.connection.get_queue(queue_name)
        return queue

    def enqueue(self, queue_name, payload):
        message = self._encode_message(payload)
        queue = self.get_queue(queue_name)
        queue.write(message)

    def dequeue(self, queue_name, visibility_timeout=None, wait_time=20):
        messages = None
        queue = self.get_queue(queue_name)

        while not messages:
            messages = queue.get_messages(
                wait_time_seconds=wait_time,
                visibility_timeout=visibility_timeout,
                attributes='All',
            )

            if not messages and wait_time == 0:
                return None  # Non-blocking mode

        payload = self._decode_message(messages[0])
        return payload

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
            'id': message.id,
            'md5': message.md5,
            'retries': retries,
            'created_on': datetime.fromtimestamp(created_on),
            'first_execution_on': datetime.fromtimestamp(first_execution_on),
        }

        return payload
