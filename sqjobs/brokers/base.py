from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Broker(object):

    @abstractmethod
    def add_job(self, job_class, *args, **kwargs):
        raise NotImplementedError
