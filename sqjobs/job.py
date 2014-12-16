from abc import ABCMeta, abstractmethod


class Job(object):
    __metaclass__ = ABCMeta

    name = None
    queue = 'sqjobs'
    retry_time = None  # use queue's default value

    def __init__(self):
        self.retries = 0
        self.created_on = None
        self.first_execution_on = None
        self._message = None

    def __repr__(self):
        return '{}()'.format(type(self).__name__)

    def next_retry(self):
        return self.retry_time

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _default_task_name(cls):
        module = cls.__module__
        name = cls.__name__
        return '{}|{}'.format(module, name)

    @classmethod
    def _task_name(cls):
        return cls.name if cls.name else cls._default_task_name()
