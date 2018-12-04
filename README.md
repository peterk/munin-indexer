# Munin - a Facebook and Instagram indexer and archiver

This tool will monitor open Facebook and Instagram account seeds for new posts and archive those posts available on the open web. Posts are archived in the WARC file format.

# Install

Create and empty data directory for postgres called data.

`$ mkdir data`

Copy `example_env_file` to env_file and update it with your settings.

Start Munin web and database to prepare migrations:

`$ docker-compose up web db -d`

Apply database migrations (when db and web has started):

`$ ./migrate.sh`

Bring up the other containers;

`$ docker-compose up -d`

Set up a superuser:

`$ docker-compose exec web python manage.py createsuperuser`

Login to the admin UI with the newly created superuser at http://0.0.0.0:4444/admin
