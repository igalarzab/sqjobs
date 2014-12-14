from abc import ABCMeta, abstractmethod


class Job(object):
    __metaclass__ = ABCMeta

    queue = 'sqjobs'
    default_retry_time = 30  # seconds

    def __init__(self):
        self.retries = 0
        self.created_on = None
        self.first_execution_on = None

    def __repr__(self):
        return '{}()'.format(type(self).__name__)

    @classmethod
    def name(cls):
        module = cls.__module__
        name = cls.__name__
        return '{}|{}'.format(module, name)

    def next_retry(self):
        return self.default_retry_time

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

