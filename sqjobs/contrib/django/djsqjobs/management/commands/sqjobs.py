from __future__ import absolute_import

from django.core.management.base import BaseCommand

from sqjobs.contrib.django.djsqjobs.finders import register_all_jobs
from sqjobs.contrib.django.djsqjobs.utils import get_worker


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
        worker = get_worker(queue_name)

        register_all_jobs(worker)
        worker.run()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs worker QUEUE_NAME')
