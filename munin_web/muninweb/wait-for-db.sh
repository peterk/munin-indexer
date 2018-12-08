#!/bin/bash

PGPASSFILE=/tmp/pgpasswd$$
echo "db:5432:$POSTGRES_DB:$POSTGRES_USER:$POSTGRES_PASSWORD" > $PGPASSFILE
chmod 600 $PGPASSFILE
export PGPASSFILE

RETRIES=10

until psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do 
    echo "Waiting for postgres server to start, $((RETRIES)) remaining attempts..." 
    RETRIES=$((RETRIES-=1)) 
    sleep 2
done

rm $PGPASSFILE
echo "Database is up! Migrating and starting web app" 

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000