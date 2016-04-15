#!/usr/bin/env python

"""
SQJobs - Simple Queue Jobs.

Usage:
  sqjobs <broker> worker [options] <queue_name>
  sqjobs (-h | --help)
  sqjobs --version

Options:
  --jobs=<module>               Python module where jobs are located [default: .jobs]

AWS SQS Options:
  --aws-access-key=<ak>         Access key to access SQS
  --aws-secret-key=<sk>         Secret key to access SQS
  --aws-region-name=<region>    AWS Region [default: us-west-1]

Utils:
  --sentry-dsn=<sentry_dsn>     Sentry DSN to report exceptions (raven must be installed)

Other options:
  -h --help              Show this screen.
  --version              Show version.
"""

import logging

from docopt import docopt

from .contrib.sentry import create_raven_client, register_sentry
from .metadata import __version__
from .utils import create_sqs_worker, get_jobs_from_module


def get_worker_config(broker, arguments):
    if broker != 'sqs':
        raise ValueError('Unknown broker: %s' % broker)

    config = {
        'access_key': arguments['--aws-access-key'],
        'secret_key': arguments['--aws-secret-key'],
        'region_name': arguments['--aws-region-name'],
    }

    if not config['access_key'] or not config['secret_key']:
        raise ValueError('--aws-access-key and --aws-secret-key are mandatory for SQS')

    return config


def config_logger(arguments):
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(message)s',
        level='INFO',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    arguments = docopt(__doc__, version=__version__)
    config_logger(arguments)

    queue_name = arguments['<queue_name>']
    worker_config = get_worker_config(arguments['<broker>'], arguments)

    worker = create_sqs_worker(
        queue_name=queue_name,
        **worker_config
    )

    for job in get_jobs_from_module(arguments['--jobs']):
        worker.register_job(job)

    if arguments['--sentry-dsn']:
        raven_client = create_raven_client(arguments['--sentry-dsn'])
        register_sentry(raven_client, worker)

    worker.run()


if __name__ == '__main__':
    main()

