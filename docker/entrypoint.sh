#!/usr/bin/env bash
set -e

# Options Django/Gunicorn
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}

echo "Apply migrations…"
python manage.py migrate --noinput

echo "Collect static…"
python manage.py collectstatic --noinput

echo "Starting Gunicorn…"
exec gunicorn config.wsgi:application \
  --config docker/gunicorn.conf.py
