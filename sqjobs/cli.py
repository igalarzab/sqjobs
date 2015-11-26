#!/usr/bin/env python

"""
SQJobs - Simple Queue Jobs.

Usage:
  sqjobs <broker> worker [options] <queue_name>
  sqjobs (-h | --help)
  sqjobs --version

AWS SQS Options:
  --aws-access-key=<ak>         Access key to access SQS
  --aws-secret-key=<sk>         Secret key to access SQS
  --aws-region=<region>         AWS Region [default: us-west-1]
  --aws-port=<port>             Port where SQS is located [default: 443]
  --aws-is-secure=<is_secure>   If the connections runs behind SSL [default: 1]

Other options:
  -h --help              Show this screen.
  --version              Show version.
"""

import logging
from docopt import docopt

from .metadata import __version__
from .worker import create_sqs_worker


def get_worker_config(broker, arguments):
    if broker != 'sqs':
        raise ValueError('Unknown broker: %s' % broker)

    config = {
        'access_key': arguments['--aws-access-key'],
        'secret_key': arguments['--aws-secret-key'],
        'region': arguments['--aws-region'],
        'port': int(arguments['--aws-port']),
        'is_secure': int(arguments['--aws-is-secure']),
    }

    if not config['access_key'] or not config['secret_key']:
        raise ValueError('--aws-access-key and --aws-secret-key are mandatory for SQS')

    return config



def main(arguments):
    queue_name = arguments['<queue_name>']
    worker_config = get_worker_config(arguments['<broker>'], arguments)

    worker = create_sqs_worker(
        queue_name=queue_name,
        **worker_config
    )

    worker.execute()


if __name__ == '__main__':
    logger = logging.getLogger('sqjobs')
    logging.basicConfig(format='[%(asctime)-15s] %(message)s', level='INFO')

    args = docopt(__doc__, version=__version__)
    main(args)
