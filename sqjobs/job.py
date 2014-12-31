from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Job(object):
    name = None
    queue = 'sqjobs'
    retry_time = None  # None means use queue's default value

    def __init__(self):
        self.id = None
        self.retries = 0
        self.created_on = None
        self.first_execution_on = None

    def __repr__(self):
        return '{0}()'.format(type(self).__name__)

    def next_retry(self):
        return self.retry_time

    def on_success(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _default_task_name(cls):
        module = cls.__module__
        name = cls.__name__
        return '{0}|{1}'.format(module, name)

    @classmethod
    def _task_name(cls):
        return cls.name if cls.name else cls._default_task_name()
