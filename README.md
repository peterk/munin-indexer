# Munin - a Facebook and Instagram indexer and archiver

This tool will monitor open Facebook and Instagram account seeds for new posts and archive those posts available on the open web. Posts are archived in the WARC file format using the excellent Squidwarc package. A playback tool and a simple dashboard is available to monitor collections.


<img src="https://user-images.githubusercontent.com/19284/49699663-3e337b80-fbd4-11e8-8282-035ea7f219ba.png" alt="Munin dashboard screenshot">

# System overview

Munin builds on great software by other people. Indexing of post items is done in [snscrape](https://github.com/JustAnotherArchivist/snscrape). Archiving of individual pages is done with [Squidwarc](https://github.com/N0taN3rd/Squidwarc). Playback of WARC files is enabled by [pywb](https://pywb.readthedocs.io/en/latest/).

<img src="https://user-images.githubusercontent.com/19284/50910349-eafc5500-142d-11e9-8028-12b818cfbf1f.png" alt="System overview - a Django application manages seeds and post URL:s in a PostgreSQL database. A queue for indexing finds more post URLs for the seeds. A queue for archiving makes sure post URLs are archived."/>

# Install

Create and empty data directory for postgres called data.

`$ mkdir data`

Copy `example_env_file` to env_file and update it with your settings.

Start everything;

`$ docker-compose up -d`

Set up a superuser:

`$ docker-compose exec web python manage.py createsuperuser`

Login to the admin dashboard with the newly created superuser at http://0.0.0.0:4444/admin

Start by adding your first Collection item in the admin interface. Then add one or more seed URLs to the collection (e.g. https://www.instagram.com/visit_berlin/). You can bulk add multiple seeds (one per line) fron the dashboard.

After a couple of minutes, archived pages are available for playback from http://0.0.0.0:4445/munin/
