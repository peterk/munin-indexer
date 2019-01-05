#!/usr/bin/env python
import os
import sys
import shutil

proj_path = "/code"


def delete_folder(warc_path):
    # job folder from warc path

    try:
        if len(warc_path.split("/")) > 6:
            path = "/".join(warc_path.split("/")[0:7])

            #move it
            print(f"Moving: {path}")
            shutil.move(path, "/deleted/")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muninweb.settings')
    sys.path.append(proj_path)
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    os.chdir(proj_path)

    from munin.models import *
    #post_id = sys.argv[1]
    #p = Post.objects.get(id=post_id)
    #print(p.warc_path)
    #shutil.copy(p.warc_path, f"/tmp/{post_id}.warc")
    #print(f"/tmp/{post_id}.warc")

    checked = set()

    print(f"Pre distinct uid: {Post.objects.all().distinct('uid').count()}")
    print(f"Total count: {Post.objects.all().count()}")

    for post in Post.objects.all():
        if post.id not in checked:
            print(f"Checking {post.id} with {post.uid}")
            pset = Post.objects.filter(uid=post.uid).order_by("warc_size")
            if pset.count() > 1:
                # at least one dupe
                for p in pset:
                    print(f"    Dupe {p.id}\t{p.uid}")
                
                print(f"Deleting all but {pset.last().id}")

                for p in pset[0:len(pset)-1]:
                    # delete warc file 
                    print(f"    Del: {p.id}")
                    delete_folder(p.warc_path)
                    checked.add(p.id)
                    # delete db object
                    p.delete()
            else:
                print(f"No dupes for {post.id}")
        else:
            print(f"Skipping {post.id}")
    
    print(f"Deleted count: {len(checked)}") 
    print(f"Pre distinct uid: {Post.objects.all().distinct('uid').count()}")