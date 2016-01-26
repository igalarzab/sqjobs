from abc import ABCMeta, abstractmethod
from six import add_metaclass
from uuid import uuid4


@add_metaclass(ABCMeta)
class Broker(object):

    @abstractmethod
    def add_job(self, job_class, *args, **kwargs):
        """
        Add a job to the broker

        :param job_class: python class of the payload job
        :param args: arguments to execute the job
        :param kwargs: keyword arguments to execute the job
        """
        raise NotImplementedError

    def gen_job_id(self):
        """
        Generate a new unique job ID
        """
        return str(uuid4())

    def serialize_job(self, job_class, job_id, args, kwargs):
        """
        Serialize a job into a string to be sent to the broker

        :param job_class: python class of the payload job
        :param job_id: the ID of the job
        :param args: arguments of the job
        :param kwargs: keyword arguments of the job
        """
        return self.connector.serialize_job(job_class, job_id, args, kwargs)

    def unserialize_job(self, job_class, queue_name, payload):
        """
        Build a job given a payload returned from the broker

        :param job_class: python class of the payload job
        :param queue_name: queue where the job was located
        :param payload: python dict with the job arguments
        """
        return self.connector.unserialize_job(job_class, queue_name, payload)
