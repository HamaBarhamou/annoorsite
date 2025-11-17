# Dockerfile.b4a — Build mono-conteneur pour Back4App
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Dépendances système (psycopg2 & Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Déps Python
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Code
COPY . /app

# Dossiers runtime (⚠️ espaces corrigés)
RUN mkdir -p /app/staticfiles /app/media && \
    adduser --disabled-password --gecos "" django || true && \
    chown -R django:django /app

USER django

# Collectstatic (ne casse pas le build si pas de static)
RUN python manage.py collectstatic --noinput || true

# Expose le port attendu par Back4App
EXPOSE 8000

# Entrée
CMD ["bash", "-lc", "python manage.py migrate --noinput \
 && python manage.py ensure_superuser \
 && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-30} --access-logfile - --error-logfile -"]
