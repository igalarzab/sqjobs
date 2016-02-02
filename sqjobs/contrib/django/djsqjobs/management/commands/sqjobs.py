from __future__ import absolute_import

from django.conf import settings
from django.core.management.base import BaseCommand

from sqjobs import create_sqs_worker
from sqjobs.contrib.django.djsqjobs.utils import register_all_jobs


class Command(BaseCommand):
    help = 'sqjobs commands'
    args = True

    def handle(self, *args, **options):
        if args[0] == 'worker':
            if len(args) != 2:
                self.help_text()
                return

            self._execute_worker(args[1])

    def _execute_worker(self, queue_name):
        worker = create_sqs_worker(
            queue_name=queue_name,
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region_name=settings.SQJOBS_SQS_REGION_NAME,
            endpoint_url=getattr(settings, 'SQJOBS_SQS_ENDPOINT_URL', None),
        )

        register_all_jobs(worker)
        worker.run()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs worker QUEUE_NAME')
