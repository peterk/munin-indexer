import time
import os
import glob
import json
import shutil
import re
import sys
from os.path import basename
import logging
import traceback
import pika
import subprocess
import requests


def get_warc_and_size(folder):
    warc_size = 0
    warc_name = ""
    for f in os.listdir(folder):
        if f.endswith(".warc"):
            warc_name = os.path.join(folder, f)
            warc_size = os.path.getsize(os.path.join(folder, f))

    return (warc_name, warc_size)



def handle_job(message):
    """Start working on a job.
    """
    logging.info(f"Started working on {message}")

    try:
        jdata = json.loads(message)
        jobid = jdata["jobid"]
        output_path = jdata["warc"]["output"]
        post_url = jdata["post_url"]
        seed_id = jdata["seed_id"]

        # make output dir
        os.makedirs(output_path, exist_ok=True)

        # write job to file in output dir
        with open(f"{output_path}/crawl_job.json", 'w') as outfile:
            json.dump(jdata, outfile)
            logging.info(f"Wrote {output_path}/crawl_job.json")

        command = f"node --harmony index.js -c {output_path}/crawl_job.json" 
        # run squidwarc
        subprocess.run(command, cwd="/usr/src/app/Squidwarc", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        warc_path, warc_size = get_warc_and_size(output_path)

        logging.info(f"Job {jobid} done!")

        r = requests.post('http://web:8000/dequeue_post/', data = {"post_url": post_url, "seed_id":seed_id, "warc_path": warc_path, "warc_size": warc_size})
        logging.info(f"Sent update for {jobid}. Post status {r.status_code}")

    except Exception as e:
        logging.error("Handle job broke", exc_info=True)
        r = requests.post('http://web:8000/dequeue_post/', data = {"post_url": post_url, "seed_id":seed_id, "last_error": e})




def callback(ch, method, properties, body):
    """Work on job from message queue."""
    logging.info(f"In callback for {body}...")
    handle_job(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    logging.info(f"Sent ack for {body}...")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting worker...")
    logging.info(f"Creds {os.environ['RABBITMQ_DEFAULT_USER']}")

    credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq', port=5672, heartbeat_interval=600, blocked_connection_timeout=300, virtual_host='/', credentials=credentials, connection_attempts=20, retry_delay=4))
    channel = connection.channel()
    channel.queue_declare(queue='archivejob', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='archivejob')
    logging.info("Started consuming queue...")
    channel.start_consuming()
