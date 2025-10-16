#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}

echo "Apply migrations…"
python manage.py migrate --noinput

echo "Collect static…"
python manage.py collectstatic --noinput

# Création auto du superuser si variables fournies
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensure Django superuser exists…"
  python manage.py shell <<'PY'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME","admin")
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {username}")
else:
    print(f"Superuser '{username}' already exists.")
PY
fi

echo "Starting Gunicorn…"
exec gunicorn config.wsgi:application --config docker/gunicorn.conf.py
