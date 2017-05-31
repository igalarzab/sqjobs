from __future__ import absolute_import

from django.core.management.base import BaseCommand

from sqjobs.contrib.django.djsqjobs.finders import register_all_jobs
from sqjobs.contrib.django.djsqjobs.utils import get_worker


class Command(BaseCommand):
    help = 'sqjobs commands'

    def add_arguments(self, parser):
        parser.add_argument("transport", default="sqs", type=str, choices=["sqs"])
        parser.add_argument("mode", default="worker", type=str, choices=["worker"])
        parser.add_argument("queue_name", type=str)


    def handle(self, *args, **options):
        self._execute_worker(options["queue_name"])

    def _execute_worker(self, queue_name):
        worker = get_worker(queue_name)

        register_all_jobs(worker)
        worker.run()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs sqs worker QUEUE_NAME')
