# Munin - a Facebook and Instagram indexer and archiver

This tool will monitor open Facebook and Instagram account seeds for new posts and archive those posts available on the open web. Posts are archived in the WARC file format using the excellent Squidwarc package. A simple dashboard is available to monitor collection.

<img src="https://user-images.githubusercontent.com/19284/49688338-a02aad00-fb10-11e8-96e2-a2705c9f2110.png" alt="Munin dashboard screenshot">

# Install

Create and empty data directory for postgres called data.

`$ mkdir data`

Copy `example_env_file` to env_file and update it with your settings.

Start everything;

`$ docker-compose up -d`

Set up a superuser:

`$ docker-compose exec web python manage.py createsuperuser`

Login to the admin dashboard with the newly created superuser at http://0.0.0.0:4444/admin
