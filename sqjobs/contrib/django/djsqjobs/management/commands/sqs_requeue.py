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

        # Get SQS resource from sqjobs broker
        sqs = get_broker().connector.connection

        # Get SQS queues
        orig_queue = sqs.get_queue_by_name(QueueName=origin)
        dest_queue = sqs.get_queue_by_name(QueueName=destination)

        # Get number of visible messages
        messages = int(orig_queue.attributes.get('ApproximateNumberOfMessages'))
        for _ in range(messages / 10):
            # We can receive at most 10 messages per call
            for message in orig_queue.receive_messages(MaxNumberOfMessages=10):
                dest_queue.send_message(MessageBody=message.body)
                message.delete()
