#!/bin/bash

python manage.py migrate

python manage.py makemigrations web
python manage.py migrate

gunicorn django_app.wsgi:application --bind 0.0.0.0:8000