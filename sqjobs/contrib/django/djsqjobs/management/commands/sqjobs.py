from __future__ import absolute_import

from django.core.management.base import BaseCommand

from sqjobs.contrib.django.djsqjobs.finders import register_all_jobs
from sqjobs.contrib.django.djsqjobs.utils import get_worker


class Command(BaseCommand):
    help = 'sqjobs commands'
    args = True

    def handle(self, *args, **options):
        if len(args) != 3 or args[0] != 'sqs' or args[1] != 'worker':
            self.help_text()
            return

        self._execute_worker(args[2])

    def _execute_worker(self, queue_name):
        worker = get_worker(queue_name)

        register_all_jobs(worker)
        worker.run()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs sqs worker QUEUE_NAME')
