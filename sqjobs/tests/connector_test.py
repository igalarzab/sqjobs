import boto3
import botocore
import pytest
import mock

from sqjobs.exceptions import QueueDoesNotExist
from ..connectors.sqs import SQS
from ..connectors.base import Connector
from ..connectors.dummy import Dummy
from .fixtures import Adder

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
            Connector.retry(dummy, 'demo', 'id', 10)

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
            raise botocore.exceptions.ClientError(error_response=error_response,
                                                  operation_name=None)
        return SQSQueue()


class SQSQueue(object):
    def send_message(self, MessageBody):
        pass


class TestSQSConnector(object):

    def create_sqs_connector(self):
        sqs_connector = SQS(access_key=SQS_ACCESS_KEY,
                            secret_key=SQS_SECRET_KEY,
                            region_name=SQS_REGION_NAME)
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

        sqs_mock.assert_called_with(aws_access_key_id=SQS_ACCESS_KEY,
                                    aws_secret_access_key=SQS_SECRET_KEY,
                                    region_name=SQS_REGION_NAME,
                                    service_name=SQS_SERVICE_NAME)


    @mock.patch.object(boto3, 'resource')
    def test_connection_created_with_endpoint_url_if_provided(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector_with_endpoint_url()

        sqs_connector.connection

        sqs_mock.assert_called_with(aws_access_key_id=SQS_ACCESS_KEY,
                                    aws_secret_access_key=SQS_SECRET_KEY,
                                    region_name=SQS_REGION_NAME,
                                    service_name=SQS_SERVICE_NAME,
                                    endpoint_url=ENDPOINT_URL)

    def test_serialize_job_returns_valid_json(self):
        sqs_connector = self.create_sqs_connector()

        serializer_expected = {
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

        assert serializer == serializer_expected

    @mock.patch.object(boto3, 'resource')
    def test_connection_enqueue_message_goes_ok(self, sqs_mock):
        sqs_mock.return_value = SQSMock()
        sqs_connector = self.create_sqs_connector()

        with mock.patch.object(SQSQueue, 'send_message') as send_message_mock:
            sqs_connector.enqueue(queue_name='my_queue',
                                  payload="{'key': value}")
            send_message_mock.assert_called_with(
                MessageBody="Insna2V5JzogdmFsdWV9Ig=="
            )

    @mock.patch.object(boto3, 'resource')
    def test_connection_enqueue_message_fails_if_no_queue_found(self, sqs_mock):
        sqs_mock.return_value = SQSMock(raise_queue_not_found=True)
        sqs_connector = self.create_sqs_connector()

        pytest.raises(QueueDoesNotExist, sqs_connector.enqueue,
                      queue_name='my_queue', payload="{}")
