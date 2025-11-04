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
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app

# Crée dossiers runtime
RUN mkdir -p /app/staticfiles /app/media && \
    adduser --disabled-password --gecos "" django && \
    chown -R django:django /app

USER django

# Collectstatic au build (évite de le refaire à chaque boot)
RUN python manage.py collectstatic --noinput || true

# Entrypoint (migrations + launch)
CMD ["bash", "-lc", "\
python manage.py migrate --noinput && \
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} --timeout ${GUNICORN_TIMEOUT:-30} --access-logfile - --error-logfile -"]
