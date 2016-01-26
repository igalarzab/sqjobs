from abc import ABCMeta, abstractmethod
from six import add_metaclass
from uuid import uuid4


@add_metaclass(ABCMeta)
class Broker(object):

    @abstractmethod
    def add_job(self, job_class, *args, **kwargs):
        raise NotImplementedError

    def gen_job_id(self):
        return str(uuid4())

    def serialize_job(self, job_class, job_id, args, kwargs):
        return self.connector.serialize_job(job_class, job_id, args, kwargs)

    def unserialize_job(self, job_class, queue_name, payload):
        return self.connector.unserialize_job(job_class, queue_name, payload)
