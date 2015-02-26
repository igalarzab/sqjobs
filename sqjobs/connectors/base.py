from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Connector(object):
    """
    Manages a single connection to the broker
    """

    @abstractmethod
    def get_queue(self, name):
        """
        Gets a queue given it name

        :param name: the name of the queue
        """
        raise NotImplementedError

    @abstractmethod
    def get_queues(self):
        """
        Gets all the queues available
        """
        raise NotImplementedError

    @abstractmethod
    def get_dead_letter_queues(self):
        """
        Gets all the dead letter queues vailable
        """
        raise NotImplementedError

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
        Receive new messages from a queue

        :param queue_name: the queue name
        :param wait_time: how much time to wait until a new message is
        retrieved (long polling). If set to zero, connection will return
        inmediately if no messages exist.
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
    def set_retry_time(self, queue_name, message_id, delay):
        """
        Changes the retry time of a message

        :param queue_name: the name of the queue
        :param message_id: the message id
        :param delay: delay (in seconds) of the next retry
        """
        raise NotImplementedError
