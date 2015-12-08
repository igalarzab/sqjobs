from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Connector(object):
    """
    Manages a single connection to the broker
    """

    @abstractmethod
    def enqueue(self, queue_name, payload):
        """
        Sends a new message to a queue

        :param queue_name: the name of the queue
        :param payload: the payload to send inside the message
        """
        raise NotImplementedError

    @abstractmethod
    def dequeue(self, queue_name, wait_time=20):
        """
        Receive the next message from a queue

        :param queue_name: the queue name
        :param wait_time: how much time to wait until a new message is retrieved (long polling).
         If set to zero, connection will return inmediately if no messages exist.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, queue_name, message_id):
        """
        Deletes a message from a queue

        :param queue_name: the name of the queue
        :param message_id: the message id
        """
        raise NotImplementedError

    @abstractmethod
    def retry(self, queue_name, message_id, delay=0):
        """
        Retry a job

        :param queue_name: the name of the queue
        :param message_id: the message id
        :param delay: delay (in seconds) when the next retry will be attempted
        """
        raise NotImplementedError

    def unseralize_job(self, job_class, queue_name, payload):
        """
        Build a job given a payload

        :param job_class: Python class of the payload job
        :param queue_name: queue where the job was located
        :param payload: Python dict with the job arguments
        """
        raise NotImplementedError
