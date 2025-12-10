FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

RUN mkdir -p /app/staticfiles /app/media && \
    adduser --disabled-password --gecos "" django || true && \
    chown -R django:django /app

USER django

# ⚠️ SUPPRIMER cette ligne (elle cassait la prod si exécutée avec un contexte incomplet)
# RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["bash", "-lc", "\
python manage.py migrate --noinput \
 && echo '== CLEAR STATICFILES ==' \
 && rm -rf /app/staticfiles/* \
 && echo '== COLLECTSTATIC ==' \
 && python manage.py collectstatic --noinput --clear -v 2 \
 && python manage.py ensure_superuser \
 && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-30} --access-logfile - --error-logfile -"]

