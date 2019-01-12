from django.core.management.base import BaseCommand, CommandError
from munin.models import *
import itertools
from django.core.paginator import Paginator

class Command(BaseCommand):
    help = 'Adjust hour of last_check for seeds to smooth crawl jobs.'

    def print_stats(self):
        s = Seed.objects.filter(last_check__isnull=False).order_by("last_check")
        groups = itertools.groupby(sorted(s, key=lambda y:y.last_check.hour), lambda x:int(x.last_check.hour))
        self.stdout.write(self.style.SUCCESS("Seeds by hour:"))
        for a, b in groups:
    	    self.stdout.write(f"{a}: {sum(1 for _ in b)}")


    def handle(self, *args, **options):

        self.print_stats()

        s = Seed.objects.filter(last_check__isnull=False).order_by("last_check")
        seeds_per_hour = round(s.count()/24.0)
        self.stdout.write(self.style.SUCCESS(f"Optimal seeds by hour: {seeds_per_hour}"))

        ps = Paginator(s, seeds_per_hour)
        self.stdout.write(self.style.SUCCESS(f"Pages: {ps.page_range}"))

        for page in ps.page_range:
            for seed in ps.page(page):
                self.stdout.write(f"Moving {seed} from {seed.last_check.hour} to {page-1}")
                seed.last_check = seed.last_check.replace(hour=page-1)
                seed.save()

        self.stdout.write(self.style.SUCCESS("After smoothing:"))
        self.print_stats()