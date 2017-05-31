from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError

from sqjobs.contrib.django.djsqjobs.utils import get_broker


class Command(BaseCommand):
    help = 'Requeue dead messages'

    def add_arguments(self, parser):
        parser.add_argument('origin')
        parser.add_argument('destination')

    def handle(self, *args, **options):
        origin = options.get('origin')
        destination = options.get('destination')

        if not origin or not destination:
            raise CommandError('Need an origin queue to requeue')

        self.stdout.write('Requeuing messages from "{}" to "{}"'.format(
            origin, destination
        ))

        messages_ok = 0
        sqs_connector = get_broker().connector
        while True:
            message = sqs_connector.dequeue(origin, wait_time=0)

            if not message:
                break

            sqs_connector.enqueue(destination, message)
            messages_ok += 1

        self.stdout.write(self.style.SUCCESS(
            'Messages processed: {}'.format(messages_ok)
        ))
