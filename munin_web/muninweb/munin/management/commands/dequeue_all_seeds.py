from django.core.management.base import BaseCommand, CommandError
from munin.models import *
import itertools
from django.core.paginator import Paginator
from datetime import datetime, timezone, timedelta

class Command(BaseCommand):
    help = 'Dequeue seeds older than two days.'

    def handle(self, *args, **options):

        s = Seed.objects.filter(state=2, last_check__lte=datetime.now(pytz.timezone(os.environ["TZ"]))-timedelta(days=2)).order_by("last_check")

        self.stdout.write(self.style.SUCCESS(f"Found {s.count()} seeds in queue older than 2 days"))

        for seed in s:
            self.stdout.write(f"Dequeueing {seed}")
            seed.state = 1
            seed.save()

        self.stdout.write(self.style.SUCCESS("Done"))