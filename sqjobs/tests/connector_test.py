import boto3
import botocore
from datetime import datetime
from pytz import timezone
import pytest
import mock

from sqjobs.exceptions import QueueDoesNotExist
from ..connectors.sqs import SQS, SQSMessage
from ..connectors.base import Connector
from ..connectors.dummy import Dummy
from .fixtures import Adder

QUEUE_NAME = 'my_queue'
SQS_SERVICE_NAME = 'sqs'
SQS_REGION_NAME = 'us-east-1'
SQS_ACCESS_KEY = 'ACCESS_KEY'
SQS_SECRET_KEY = 'SECRET_KEY'
ENDPOINT_URL = 'my_url'


class TestConnectorInterface(object):

    def test_default_connector_interface(self):
        dummy = Dummy()

        with pytest.raises(NotImplementedError):
            Connector.enqueue(dummy, 'demo', {})

        with pytest.raises(NotImplementedError):
            Connector.dequeue(dummy, 'demo', wait_time=20)

        with pytest.raises(NotImplementedError):
            Connector.delete(dummy, 'demo', 'id')

        with pytest.raises(NotImplementedError):
            Connector.set_retry_time(dummy, 'demo', 'id', 10)

        with pytest.raises(NotImplementedError):
            Connector.serialize_job(dummy, dummy, 'job_id', 'args', {})

        with pytest.raises(NotImplementedError):
            Connector.unserialize_job(dummy, dummy, 'demo', 'payload')


class SQSMock(object):
    def __init__(self, raise_queue_not_found=False):
        self.raise_queue_not_found = raise_queue_not_found

    def get_queue_by_name(self, QueueName):
        if self.raise_queue_not_found:
            error_response = {'Error': {}}

            raise botocore.exceptions.ClientError(
                error_response=error_response,
                operation_name=None
            )

        return SQSQueueMock()


class SQSQueueMock(object):
    def send_message(self, MessageBody):
        pass

    def receive_messages(self, MaxNumberOfMessages, WaitTimeSeconds, AttributeNames):
        pass

    def delete_messages(self):
        pass

    def change_message_visibility_batch(self):
        pass


class SQSMessageMock(object):

    def __init__(self, receipt_handle="1"):
        self.body = SQSMessage.encode({'key': 'value'})
        self.receipt_handle = receipt_handle
        self.attributes = {
            "ApproximateReceiveCount": 0,
            "SentTimestamp": 1460186204000
        }


class TestSQSConnector(object):

    def create_sqs_connector(self):
        sqs_connector = SQS(
            access_key=SQS_ACCESS_KEY,
            secret_key=SQS_SECRET_KEY,
            region_name=SQS_REGION_NAME
        )

        return sqs_connector

    def create_sqs_connector_with_endpoint_url(self):
        sqs_connector = self.create_sqs_connector()
        sqs_connector.endpoint_url = ENDPOINT_URL
        return sqs_connector

    @mock.patch.object(boto3, 'resource')
    def test_connection_is_cached(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        sqs_connector.connection

        assert sqs_connector._cached_connection is not None

    @mock.patch.object(boto3, 'resource')
    def test_connection_created_with_aws_parameters(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        sqs_connector.connection

        sqs_mock.assert_called_with(
            aws_access_key_id=SQS_ACCESS_KEY,
            aws_secret_access_key=SQS_SECRET_KEY,
            region_name=SQS_REGION_NAME,
            service_name=SQS_SERVICE_NAME
        )

    @mock.patch.object(boto3, 'resource')
    def test_connection_created_with_endpoint_url_if_provided(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector_with_endpoint_url()

        sqs_connector.connection

        sqs_mock.assert_called_with(
            aws_access_key_id=SQS_ACCESS_KEY,
            aws_secret_access_key=SQS_SECRET_KEY,
            region_name=SQS_REGION_NAME,
            service_name=SQS_SERVICE_NAME,
            endpoint_url=ENDPOINT_URL
        )

    def test_serialize_job_returns_valid_json(self):
        sqs_connector = self.create_sqs_connector()

        expected_serializer = {
            'args': [3, 4],
            'id': 15,
            'kwargs': {'first_param': 1, 'second_param': 'two'},
            'name': 'adder'
        }

        serializer = sqs_connector.serialize_job(
            job_class=Adder,
            job_id=15,
            args=[3, 4],
            kwargs={'first_param': 1, 'second_param': 'two'}
        )

        assert serializer == expected_serializer

    def test_unserialize_job_returns_job_class(self):
        sqs_connector = self.create_sqs_connector()

        payload = {
            'id': 1,
            '_metadata': {
                'created_on': datetime(2016, 4, 9, 7, 16, 44, tzinfo=timezone('UTC')),
                'id': '1',
                'retries': 0
            },
            'args': [1, 'second_arg'],
            'kwargs': {
                'first_kwarg': 1,
                'second_kwarg': '2'
            }
        }

        job, args, kwargs = sqs_connector.unserialize_job(
            job_class=Adder,
            queue_name=QUEUE_NAME,
            payload=payload
        )

        assert isinstance(job, Adder) is True
        assert args == [1, 'second_arg']
        assert kwargs == {'first_kwarg': 1, 'second_kwarg': '2'}

    @mock.patch.object(boto3, 'resource')
    def test_connection_enqueue_message_goes_ok(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueueMock, 'send_message') as send_message_mock:
            sqs_connector.enqueue(queue_name=('%s' % QUEUE_NAME), payload="{'key': value}")
            send_message_mock.assert_called_with(
                MessageBody="Insna2V5JzogdmFsdWV9Ig=="
            )

    @mock.patch.object(boto3, 'resource')
    def test_connection_enqueue_message_fails_if_no_queue_found(self, sqs_mock):
        sqs_mock.return_value = SQSMock(raise_queue_not_found=True)
        sqs_connector = self.create_sqs_connector()

        pytest.raises(QueueDoesNotExist, sqs_connector.enqueue, queue_name=QUEUE_NAME, payload="{}")

    @mock.patch.object(boto3, 'resource')
    def test_connection_dequeue_message_goes_ok(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        expected_payload = {
            '_metadata': {
                'created_on': datetime(2016, 4, 9, 7, 16, 44, tzinfo=timezone('UTC')),
                'id': '1',
                'retries': 0
            },
            'key': 'value'
        }

        with mock.patch.object(SQSQueueMock, 'receive_messages') as receive_messages_mock:
            receive_messages_mock.return_value = [
                SQSMessageMock(receipt_handle="1"),
                SQSMessageMock(receipt_handle="2")
            ]

            payload = sqs_connector.dequeue(QUEUE_NAME)

            receive_messages_mock.assert_called_with(
                AttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

        assert payload == expected_payload

    @mock.patch.object(boto3, 'resource')
    def test_connection_dequeue_message_fails_if_no_queue_found(self, sqs_mock):
        sqs_mock.return_value = SQSMock(raise_queue_not_found=True)
        sqs_connector = self.create_sqs_connector()

        pytest.raises(QueueDoesNotExist, sqs_connector.dequeue, queue_name=QUEUE_NAME)

    @mock.patch.object(boto3, 'resource')
    def test_connection_dequeue_message_with_wait_time(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueueMock, 'receive_messages') as receive_messages_mock:
            receive_messages_mock.return_value = [SQSMessageMock()]

            sqs_connector.dequeue(QUEUE_NAME, wait_time=10)

            receive_messages_mock.assert_called_with(
                AttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )

    @mock.patch.object(boto3, 'resource')
    def test_connection_dequeue_message_non_blocking_mode(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueueMock, 'receive_messages') as receive_messages_mock:
            receive_messages_mock.return_value = []

            payload = sqs_connector.dequeue(QUEUE_NAME, wait_time=0)

            assert payload is None

    @mock.patch.object(boto3, 'resource')
    def test_connection_delete_message_goes_ok(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueueMock, 'delete_messages') as delete_messages_mock:

            sqs_connector.delete(QUEUE_NAME, message_id=1)

            delete_messages_mock.assert_called_with(
                Entries=[
                    {
                        'Id': '1',
                        'ReceiptHandle': 1
                    }
                ]
            )

    @mock.patch.object(boto3, 'resource')
    def test_connection_delete_message_fails_if_no_queue_found(self, sqs_mock):
        sqs_mock.return_value = SQSMock(raise_queue_not_found=True)
        sqs_connector = self.create_sqs_connector()

        pytest.raises(QueueDoesNotExist, sqs_connector.delete, queue_name=QUEUE_NAME, message_id=1)

    @mock.patch.object(boto3, 'resource')
    def test_connection_retry_message_goes_ok(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueueMock, 'change_message_visibility_batch') as change_mock:

            sqs_connector.set_retry_time(QUEUE_NAME, message_id=5, delay=1)

            change_mock.assert_called_with(
                Entries=[
                    {
                        'Id': '1',
                        'ReceiptHandle': 5,
                        'VisibilityTimeout': 1
                    }
                ]
            )

            sqs_connector.set_retry_time(QUEUE_NAME, message_id=5, delay=None)

            change_mock.assert_called_with(
                Entries=[
                    {
                        'Id': '1',
                        'ReceiptHandle': 5,
                        'VisibilityTimeout': 0
                    }
                ]
            )

    @mock.patch.object(boto3, 'resource')
    def test_connection_retry_message_fails_if_no_queue_found(self, sqs_mock):
        sqs_mock.return_value = SQSMock(raise_queue_not_found=True)
        sqs_connector = self.create_sqs_connector()

        pytest.raises(
            QueueDoesNotExist,
            sqs_connector.set_retry_time,
            queue_name=QUEUE_NAME,
            message_id=1,
            delay=1
        )
