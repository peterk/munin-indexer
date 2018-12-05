import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from munin.models import *
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


@register_job(scheduler, "interval", seconds=60, replace_existing=True)
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
            if datetime.now(pytz.timezone('Europe/Stockholm')) > (seed.last_check + timedelta(seconds=seed.check_frequency)):
                print(datetime.now())
                print(seed.last_check)
                print(seed.check_frequency)
                seed.enqueue()
            else:
                #not yet
                print(f"Not yet time for seed {seed.id}: {seed.seed}")


@register_job(scheduler, "interval", seconds=120, replace_existing=True)
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
            if datetime.now(pytz.timezone('Europe/Stockholm')) > (post.last_crawled_at + timedelta(seconds=600)):
                post.enqueue()
            else:
                #not yet
                print(f"Not yet time for post url {post.id}: {post.url}, time: {post.last_crawled_at}")



register_events(scheduler)

scheduler.start()
print("Scheduler started!")
