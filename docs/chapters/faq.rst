Frequently asked questions (FAQ)
================================

If you have any question that is not answered here please feel free to create a `new issue in Github
<https://github.com/igalarzab/sqjobs/issues/new?labels=question>`_ and we'll add the answer here.


Which brokers are supported by SQJobs?
--------------------------------------

`SQS <https://aws.amazon.com/sqs/>`_ is the only supported broker by SQJobs now.

Anyway, create new brokers is an easy task, just check the `base broker
<https://github.com/igalarzab/sqjobs/blob/master/sqjobs/brokers/base.py>`_ to have an idea of how
to create a new one.


How do I execute more than one job at a time?
---------------------------------------------

SQJobs follows the `KISS <https://en.wikipedia.org/wiki/KISS_principle>`_ principle and the
`UNIX philosophy <https://en.wikipedia.org/wiki/Unix_philosophy>`_, trying to do just one thing in
the best possible way.

In that manner, SQJobs doesn't provide a way to execute parallell workers, delegating that task to
specific process managers like *supervisor*, *circus*, *upstart*, ...

As an example, here is a sample configuration for circus::

    [watcher:sqjobs]
    working_dir = /opt/project/src
    cmd = sqjobs sqs worker downloader --aws-access-key=AK --aws-secret-key=SK --jobs=jobs
    numprocesses = 4
    uid = sqjobs
    autostart = True


I don't see any feedback when I'm executing the worker from Django
------------------------------------------------------------------

When using the worker from django (with the ``manage.py`` script) SQJobs doesn't print anything in
the stdout/stderr. As a good practise, it uses the standard logging system of Python to provide you
useful information about what's happening.

To see this information you need to configure the django logging system. There is `plenty of
information <https://docs.djangoproject.com/en/dev/topics/logging/>`_ about how to do it, but here
is an example of the ``settings.py`` to export DEBUG information to the standard output (usually,
your shell)::

    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'sqjobs': {  # This is the name of the logger where SQJobs writes it information
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
