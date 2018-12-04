# Munin - a Facebook and Instagram indexer and archiver




# Crawler



# Install

Create and empty data directory for postgres called data.
`$ mkdir data`

Copy example_env_file to env_file and update it with your settings.

Start Munin:
`$ docker-compose up -d`

Apply database migrations (when db and web has started):
`$ ./migrate.sh`

Set up a superuser:
`$ docker-compose exec web python manage.py createsuperuser`

Login to the admin UI with the newly created superuser at 0.0.0.0:4444/admin
