from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from munin.models import *
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):

    if not request.user.is_authenticated:
         return HttpResponseForbidden()
    
    collections = Collection.objects.all()

    if request.POST:
        seedstxt =  request.POST.get("seeds")
        collection_id = int(request.POST.get("collection"))
        
        if not collection_id > 0:
            messages.error(request, 'No collection selected.')
            return render(request, 'index.html', context={"collections":collections}) 
        
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
    

    return render(request, 'index.html', context={"collections":collections})



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
