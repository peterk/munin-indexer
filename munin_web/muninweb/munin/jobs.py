import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from munin.models import *
from datetime import datetime, timedelta
from django.utils import timezone
import os
import pytz

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

@register_job(scheduler, "interval", seconds=3600, replace_existing=True)
def queue_stat():

    stat = Stats()
    now = datetime.now(pytz.timezone(os.environ["TZ"]))
    last_hr_timedelta = now - timedelta(hours=1)

    stat.warcs_created = Post.objects.filter(state=1, warc_size__gt=0, created_at__gt=last_hr_timedelta).count()
    stat.post_crawl_queue = Post.objects.filter(state=2).count()
    stat.seed_crawl_queue = Seed.objects.filter(state=2).count()

    warc_size = Post.objects.filter(created_at__gt=last_hr_timedelta).aggregate(Sum("warc_size"))["warc_size__sum"]
    if warc_size:
        stat.warc_size_total = round(warc_size / 1024 / 1024 / 1024, 2)

    stat.retry_count = Post.objects.filter(retry_count__gt=1, created_at__gt=last_hr_timedelta).count()
    stat.seed_count = Seed.objects.filter(state=2).count()
    stat.post_count = Post.objects.filter(state=1).count()
    stat.save()
    print("Saved stats item")


@register_job(scheduler, "interval", seconds=63, replace_existing=True)
def queue_crawls():
    """Check all seeds currently not in queue status, compare last_check time
    with check_frequency and add them to seed queue. Seeds will be crawled for links to posts."""

    print("In scheduler for seeds archiving")
    seeds = Seed.objects.exclude(state=2)

    for seed in seeds:
        if not seed.last_check:
            #new seed - add it immediately
            seed.enqueue()
        else:
            now = datetime.now(pytz.timezone(os.environ["TZ"])) 
            print(f"Comparing {now} to {seed.last_check}")
            if now > (seed.last_check + timedelta(seconds=seed.check_frequency)):
                print(datetime.now())
                print(seed.last_check)
                print(seed.check_frequency)
                seed.enqueue()
            else:
                #not yet
                print(f"Not yet time for seed {seed.id}: {seed.seed}")


@register_job(scheduler, "interval", seconds=127, replace_existing=True)
def queue_archiving():
    """Check which posts that haven't been archived yet and push them to the queue."""

    print("In scheduler for posts archiving")
    
    posts = Post.objects.filter(state=1, warc_path=None)
    print(f"Found {len(posts)} for archiving.")

    for post in posts:
        if not post.last_crawled_at:
            #new post - add it immediately
            post.enqueue()
        else:
            if datetime.now(pytz.timezone(os.environ["TZ"])) > (post.last_crawled_at + timedelta(seconds=600)):
                post.enqueue()
            else:
                #not yet
                print(f"Not yet time for post url {post.id}: {post.url}, time: {post.last_crawled_at}")



register_events(scheduler)

scheduler.start()
print("Scheduler started!")
