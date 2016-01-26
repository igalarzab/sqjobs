from abc import ABCMeta, abstractmethod
from six import add_metaclass

from .exceptions import RetryException


@add_metaclass(ABCMeta)
class Job(object):
    """
    A simple queue job.

    Class attributes:
        * name: Name of the job. This name must be as unique as possible. Workers will decide
          which code to execute based on this name.
        * default_queue_name: Queue name where the job will be executed if one is not specified
          when adding the job to the broker.
        * abstract: Jobs marked as abstract will not be included by workers.
        * retry_time: Time (in seconds) used to define how long the message will be locked
          until other worker could retry the job. If None, it will use the queue's default value.

    Object attributes:
        * id: Unique ID of the job.
        * broker_id: Unique ID of the job given by the broker.
        * queue_name: Queue where the job has been added.
        * retries: How many retries has been done by the job.
        * created_on: When the job was enqueued for the first time.
    """
    name = None
    default_queue_name = 'sqjobs'
    abstract = False
    retry_time = None

    def __init__(self):
        self.id = None
        self.broker_id = None
        self.queue_name = None
        self.retries = 0
        self.created_on = None

    def __repr__(self):
        return '{0}()'.format(type(self).__name__)

    def pre_run(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def post_run(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        self.pre_run(*args, **kwargs)
        res = self.result = self.run(*args, **kwargs)
        self.post_run(*args, **kwargs)

        return res

    def on_success(self):
        pass

    def on_failure(self):
        pass

    def on_retry(self):
        pass

    def retry(self):
        raise RetryException

    def next_retry_time(self):
        return self.retry_time

    @classmethod
    def _task_name(cls):
        name = cls.name

        if not name:
            name = '{0}|{1}'.format(cls.__module__, cls.__name__)

        return name


class JobResult(object):
    """
    Result of adding a job to a broker.

    Object attributes:
        * job_id: Unique ID of the job.
        * broker_id: Unique ID of the job given by the broker.
        * result: Result of the execution (used by Eager mode).
    """

    def __init__(self):
        self.job_id = None
        self.broker_id = None
        self.result = None
