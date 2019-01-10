import os
import json
import shutil
import re
import sys
from os.path import basename
import logging
import traceback
import pika

import snscrape.base
import snscrape.modules
from urllib.parse import urlparse
import requests

MAX_POSTS = 100

no_proxies = {
  "http": None,
  "https": None,
}

def get_scraper_from_seed_url(seed_url):
    scraper = None
    user = None

    o = urlparse(seed_url)

    user = o.path.replace("/","")
    print(f"User: {user}")

    if "instagram" in o.netloc:
        return snscrape.modules.instagram.InstagramUserScraper(username=user)
    elif "facebook" in o.netloc:
        return snscrape.modules.facebook.FacebookUserScraper(username=user)
    else:
        return None




def handle_job(message):
    """Look for new posts for seed.
    """
    logging.info(f"Started working on {message}")

    try:
        jdata = json.loads(message)
        seed_url = jdata["seed_url"]

        scraper = get_scraper_from_seed_url(seed_url)

        for i, item in enumerate(scraper.get_items(), start=1):
            r = requests.post('http://web:8000/add_post/', proxies=no_proxies, data = {"seed_url": seed_url, 'post_url': item})
            logging.info(f"Status {r.status_code} for {seed_url}: #{i} {item}")

            if i > MAX_POSTS or r.status_code == requests.codes.forbidden:
                logging.info("Stopping because max count or previous post reached")
                break

        logging.info(f"Job for {seed_url} done!")

    except Exception:
        logging.error("Handle seed job broke :-(", exc_info=True)
    finally:
        logging.info(f"Dequeueing {seed_url}")
        r = requests.post('http://web:8000/dequeue_seed/', proxies=no_proxies, data = {"seed_url": seed_url})
        logging.info(f"Status: {r.status_code}")



def callback(ch, method, properties, body):
    """Work on job from message queue."""
    logging.info(f"In callback for {body}...")
    handle_job(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    logging.info(f"Sent ack for seed job {body}...")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting seed worker...")
    logging.info(f"Creds {os.environ['RABBITMQ_DEFAULT_USER']}")

    credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq', port=5672, heartbeat=600, blocked_connection_timeout=300, virtual_host='/', credentials=credentials, connection_attempts=20, retry_delay=4))
    channel = connection.channel()
    channel.queue_declare(queue='indexjob', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='indexjob')
    logging.info("Started consuming seed index queue...")
    channel.start_consuming()
