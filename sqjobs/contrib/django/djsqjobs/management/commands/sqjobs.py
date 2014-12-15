from __future__ import absolute_import

from django.conf import settings
from django.core.management.base import BaseCommand

from sqjobs import create_sqs_worker


class Command(BaseCommand):
    help = 'sqjobs commands'

    def handle(self, *args, **options):
        if len(args) != 2:
            self.help_text()
            return

        if args[0] == 'worker':
            self._execute_worker(args[1])

    def _execute_worker(self, queue_name):
        worker = create_sqs_worker(
            queue_name=queue_name,
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region=settings.SQJOBS_SQS_REGION,
        )

        for job in getattr(settings, 'SQJOBS_JOBS', []):
            worker.register_job(job)

        worker.execute()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs worker QUEUE_NAME')
