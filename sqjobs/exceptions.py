class SQJobsException(Exception):
    """
    Base class for all the sqjobs exceptions
    """


class RetryException(SQJobsException):
    """
    Exception to raise when a retry is needed
    """


class QueueDoesNotExist(SQJobsException):
    """
    A queue does not exist in the broker
    """
