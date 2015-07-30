from __future__ import absolute_import

from django.conf import settings
from django.core.management.base import BaseCommand

from sqjobs import create_sqs_worker, create_sqs_broker
from sqjobs.contrib.django.djsqjobs.utils import register_all_jobs

from sqjobs.contrib.django.djsqjobs.beat import Beat


class Command(BaseCommand):
    help = 'sqjobs commands'

    def handle(self, *args, **options):
        if len(args) < 2:
            self.help_text()
            return

        if args[0] == 'worker':
            self._execute_worker(args[1])

        elif args[0] == 'beat':
            self._execute_beat(*args[1:])

    def _execute_worker(self, queue_name):
        worker = create_sqs_worker(
            queue_name=queue_name,
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region=settings.SQJOBS_SQS_REGION,
            is_secure=getattr(settings, 'SQJOBS_SQS_IS_SECURE', True),
            port=getattr(settings, 'SQJOBS_SQS_CONNECTION_PORT', 443),
        )

        register_all_jobs(worker)
        worker.execute()

    def _execute_beat(self, sleep_interval, skip_jobs=None):
        broker = create_sqs_broker(
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region=settings.SQJOBS_SQS_REGION,
            is_secure=getattr(settings, 'SQJOBS_SQS_IS_SECURE', True),
            port=getattr(settings, 'SQJOBS_SQS_CONNECTION_PORT', 443),
        )
        if skip_jobs is not None:
            skip_jobs = bool(skip_jobs)
        beat = Beat(broker, int(sleep_interval), skip_jobs)
        register_all_jobs(beat)
        beat.run_forever()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs worker QUEUE_NAME')
        self.stdout.write('./manage.py sqjobs beat SLEEP_INTERVAL [SKIP_JOBS]')
