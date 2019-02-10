from django.core.management.base import BaseCommand, CommandError
from munin.models import *
from datetime import datetime, timezone, timedelta
import pika

class Command(BaseCommand):
    help = 'Delete RabbitMq indexing queue.'

    def handle(self, *args, **options):

        credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
        connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat=600, blocked_connection_timeout=300))
        channel = connection.channel()
        channel.queue_delete(queue='indexjob')
        connection.close()
        self.stdout.write(self.style.SUCCESS("Deleted index job queue"))