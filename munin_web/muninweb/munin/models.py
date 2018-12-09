from django.db import models
import pika
import json
import os
from datetime import datetime, timezone
import pytz
import hashlib
from hashlib import md5
from django.db.models import Avg, Max, Min, Sum

class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        return self.name


SEED_QUEUE_STATES = ( (1, 'Waiting'), (2, 'In queue') )


class Seed(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    seed = models.URLField(max_length=4000, db_index=True)
    last_check = models.DateTimeField(blank=True, null=True)
    state = models.PositiveIntegerField(choices=SEED_QUEUE_STATES, default=1)
    created_at = models.DateTimeField(auto_now_add=True,)
    check_frequency = models.PositiveIntegerField(default=86400)

    def enqueue(self):
        """Put into discovery queue."""
        print(f"Putting {self.id} {self.seed} into discovery queue")

        jd = dict()
        jd["seed_url"] = self.seed
        jd["collection_id"] = self.collection.id
        message = json.dumps(jd)

        credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
        connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat=600, blocked_connection_timeout=300))
        channel = connection.channel()
        channel.queue_declare(queue='indexjob', durable=True)
        channel.basic_publish(exchange='', routing_key='indexjob', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
        connection.close()

        print(f"Created job {message}")

        # hold state until indexing has completed
        self.state = 2
        self.save()


    def dequeue(self):
        print(f"Moving {self.id} {self.seed} out of discovery queue")

        self.last_check = datetime.now(pytz.timezone(os.environ["TZ"]))
        self.state = 1
        self.save()

    def __str__(self):
        return self.seed.replace("https://","")


class Post(models.Model):
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)
    url = models.URLField(max_length=4000, db_index=True, unique=True)
    state = models.PositiveIntegerField(choices=SEED_QUEUE_STATES, default=1)
    warc_path = models.TextField(blank=True, null=True)
    warc_size = models.PositiveIntegerField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    last_crawled_at = models.DateTimeField(db_index=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    jobid = models.CharField(max_length=200, blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)


    def make_job(self, jobid, output_path, description=""):
        """Create json for crawl job.
        """

        print(f"Writing to {output_path}")

        data = {}
        data["jobid"] = jobid
        data["description"] = description

        # create concatenated script file for this job.
        scripts = ["scroll_everything.js", "srcset.js", "video_src_load.js"]

        if scripts:
            os.mkdir(os.path.join("/", "jobs", jobid))
            jobscript_file = os.path.join("/", "jobs", jobid, "jobscript.js")
            with open(jobscript_file, 'w') as outfile:
    
                # add utils
                outfile.write("const utils = require(\"/scripts/utils/utils\");\n")
    
                # write methods. Each script file should contain a function with the same name as the script file.
                for script in scripts:
                    with open(f"/scripts/{script}") as infile:
                        outfile.write(infile.read())
    
                ## write method calls
                outfile.write("\n\nmodule.exports = async function (page) {\n")
                for script in scripts:
                    function_call = "\tawait " + script.replace(".js","") + "(page);"
                    outfile.write(function_call + "\n")
                    outfile.write("\tawait utils.delay(2000);\n")
                outfile.write("}\n")
                
            data["script"] = jobscript_file
    
        data["use"] = "puppeteer"
        data["headless"] = True
        data["mode"] = "page-only"
        data["depth"] = 1
        data["post_url"] = self.url
        data["seed_id"] = self.seed.id
        data["seeds"] = [self.url,]
        data["warc"] = {}
        data["warc"]["naming"] = "url"
        data["warc"]["output"] = output_path
        data["warc"]["append"] = True
        data["executablePath"] = "/usr/bin/google-chrome-stable"
        data["connect"] = {}
        data["connect"]["launch"] = True
        data["connect"]["host"] = "localhost"
        data["connect"]["port"] = 9222
        data["crawlControl"] = {}
        data["crawlControl"]["globalWait"] = 60000
        data["crawlControl"]["inflightIdle"] = 2000
        data["crawlControl"]["numInflight"] = 2
        data["crawlControl"]["navWait"] = 8000

        return json.dumps(data)


    def enqueue(self):
        """Put into discovery queue."""
        print(f"Putting {self.id} {self.url} into discovery queue")

        # Make jobid from url and timestamp
        now = datetime.now(pytz.timezone(os.environ["TZ"]))
        m = hashlib.md5()
        m.update(self.url.encode("utf-8") + now.isoformat().encode("utf-8"))
        jobid = m.hexdigest()

        # Users can map /archive in docker to access warcs.
        output_path = os.path.join("/", "archive", str(self.seed.id), str(now.year), str(now.month).zfill(2), str(now.day).zfill(2), jobid)

        message = self.make_job(jobid=jobid, output_path=output_path)
        self.jobid = jobid

        credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
        connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat=600, blocked_connection_timeout=300))
        channel = connection.channel()
        channel.queue_declare(queue='archivejob', durable=True)
        channel.basic_publish(exchange='', routing_key='archivejob', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
        connection.close()

        print(f"Created job for {self.url}")
        print(f"Created archive job {message}")

        # hold state until indexing has completed
        self.state = 2

        # update retry count
        self.retry_count += 1
        self.save()


    def dequeue(self, warc_path, warc_size, last_error=None):
        print(f"Dequeueing {self.id} {self.url}")

        self.last_crawled_at = datetime.now(pytz.timezone(os.environ["TZ"]))
        if last_error:
            self.last_error = last_error
        else:
            self.warc_path = warc_path
            self.warc_size = warc_size
        self.state = 1
        self.save()

    def short_url(self):
        return str(self)[:100]


    def warc_size_kb(self):
        if self.warc_size:
            return int(self.warc_size / 1024)


    def __str__(self):
        return self.url.replace("https://","").replace("http://","")


class Stats(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,)
    warc_count = models.PositiveIntegerField(default=0)
    warcs_created = models.PositiveIntegerField(default=0)
    post_crawl_queue = models.PositiveIntegerField(default=0)
    seed_crawl_queue = models.PositiveIntegerField(default=0)
    warc_size_total = models.FloatField(default=0.0)
    retry_count = models.PositiveIntegerField(default=0)
    seed_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)