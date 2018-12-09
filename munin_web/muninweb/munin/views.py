from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from munin.models import *
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import subprocess
import pytz
import os
from datetime import datetime, timezone, timedelta
import math


@login_required
def bulk_add(request):

    collections = Collection.objects.all()

    if request.POST:
        seedstxt =  request.POST.get("seeds")
        collection_id = int(request.POST.get("collection"))
        
        if not collection_id > 0:
            messages.error(request, 'No collection selected.')
            return render(request, 'bulk_add.html', context={"collections":collections}) 
        
        count = 0

        for seed in seedstxt.splitlines():
            try:
                obj = Seed.objects.get(seed=seed.strip())
                print("Skipping " + seed)
            except Seed.DoesNotExist:
                obj = Seed(seed=seed.strip(), collection_id=collection_id)
                obj.save()
                count += 1
                print("Added " + seed)

        messages.success(request, f"Added {count} seeds for collection {collection_id}")

    return render(request, 'bulk_add.html', context=locals())


@login_required
def index(request):

    #stats for dashboard - also see chart script below
    post_queue_length = Post.objects.filter(state=2).count()
    seed_queue_length = Seed.objects.filter(state=2).count()

    warc_file_count = Post.objects.filter(state=1, warc_size__gt=0).count() 

    warc_size_sum = Post.objects.aggregate(Sum("warc_size"))["warc_size__sum"] or 0
    archive_size = round(warc_size_sum / 1024 / 1024 / 1024, 1)

    now = datetime.now(pytz.timezone(os.environ["TZ"]))
    last_week_timedelta = datetime.now() - timedelta(days=7)

    last_posts = Post.objects.filter(state=1, last_crawled_at__gt=last_week_timedelta).order_by("-last_crawled_at")[:10]

    crawl_error_count = Post.objects.exclude(last_error__isnull=True).exclude(last_error__exact="").count()

    return render(request, 'dashboard.html', context=locals())


@login_required
def chart_script(request):
    now = datetime.now(pytz.timezone(os.environ["TZ"]))
    last_week_timedelta = datetime.now() - timedelta(days=7)
    stats = Stats.objects.all().order_by("id")[:168] # last 7 days worth of stat items (24 x 7)

    if len(stats) > 0:
        post_queue_last7 = [stat.post_crawl_queue for stat in stats]
        post_queue_last7_max = int(max(post_queue_last7) + max(post_queue_last7) *0.1)

        seed_queue_last7 = [stat.seed_crawl_queue for stat in stats]
        seed_queue_last7_max = int(max(seed_queue_last7) + max(seed_queue_last7) *0.1)

        warcs_created_last7 = [stat.warcs_created for stat in stats]
        stat_labels = [stat.created_at.hour for stat in stats]
        warcs_created_last7_max = int(max(warcs_created_last7) + max(warcs_created_last7) *0.1)

        chart_max = int(math.ceil(max([post_queue_last7_max, warcs_created_last7_max, seed_queue_last7_max]) / 100.0)) * 100
        return render(request, 'chart_script.js',  content_type="text/javascript", context=locals())
    else:
        return HttpResponse("No stats yet")



@csrf_exempt
@require_http_methods(["POST"])
def add_post_url_for_seed(request, seed_id=None):

    try:
        seed = Seed.objects.get(pk=seed_id)
    except Seed.DoesNotExist:
        raise Http404("No Seed matches the given query.")

    # add url if it doesnt exist already
    try:
        post_url = request.POST.get("post_url")
        post = Post.objects.get(seed=seed, url=post_url)
    except Post.DoesNotExist:
        p = Post(seed=seed, url=post_url)
        p.save()
        return HttpResponse(f"New post url: {post_url}")
    except Exception:
        raise Http404("No post url.")
    
    return HttpResponseForbidden(f"Already exists: {post_url}")


@csrf_exempt
@require_http_methods(["POST"])
def add_post_url(request):

    try:
        seed_url = request.POST.get("seed_url")
        seed = Seed.objects.get(seed=seed_url)
    except Seed.DoesNotExist:
        raise Http404("No Seed matches the given query.")

    try:
        post_url = request.POST.get("post_url")
        post = Post.objects.get(seed=seed, url=post_url)
    except Post.DoesNotExist:
        p = Post(seed=seed, url=post_url)
        p.save()
        return HttpResponse(f"New post url: {post_url}")
    except Exception:
        raise Http404("No post url.")
    
    return HttpResponseForbidden(f"Already exists: {post_url} for {seed}")



@csrf_exempt
@require_http_methods(["POST"])
def dequeue_seed(request):

    try:
        seed_url = request.POST.get("seed_url")
        seed = Seed.objects.get(seed=seed_url)
        seed.dequeue()
    except Seed.DoesNotExist:
        raise Http404("No Seed matches the given query.")

    return HttpResponse(f"Dequeued: {seed_url}")



@csrf_exempt
@require_http_methods(["POST"])
def dequeue_post_url(request):

    try:
        post_url = request.POST.get("post_url")
        seed_id = request.POST.get("seed_id")
        warc_path = request.POST.get("warc_path")
        warc_size = request.POST.get("warc_size")
        last_error = request.POST.get("last_error")
        seed = Seed.objects.get(id=int(seed_id))
        post = Post.objects.get(seed=seed, url=post_url)

        post.dequeue(warc_path=warc_path, warc_size=warc_size, last_error=last_error)

    except Seed.DoesNotExist:
        raise Http404("No Seed matches the given query.")
    except Post.DoesNotExist:
        raise Http404("No Post matches the given query.")
    except Exception as e: print(e)

    return HttpResponse(f"Dequeued: {post_url}")
