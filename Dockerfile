FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Dépendances système de base + outils diag TLS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    ca-certificates curl openssl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt \
 && python -m pip install --upgrade --no-cache-dir certifi

COPY . /app

RUN mkdir -p /app/staticfiles /app/media && \
    adduser --disabled-password --gecos "" django || true && \
    chown -R django:django /app

USER django

EXPOSE 8000

# Au démarrage :
# - on expose le bundle CA certifi à Python/botocore
# - on vérifie le TLS vers l’endpoint R2
# - migrations + collectstatic + gunicorn
CMD ["bash", "-lc", "\
python - <<'PY'\n\
import certifi, ssl; print('certifi:', certifi.where()); print('OpenSSL:', ssl.OPENSSL_VERSION)\n\
PY\n\
export SSL_CERT_FILE=$(python -c 'import certifi; print(certifi.where())') && \
export AWS_CA_BUNDLE=\"$SSL_CERT_FILE\" && \
python manage.py migrate --noinput && \
echo '== CLEAR STATICFILES ==' && rm -rf /app/staticfiles/* && \
echo '== CURL R2 HEAD ==' && curl -I ${R2_ENDPOINT:-https://example.invalid} || true && \
echo '== COLLECTSTATIC ==' && python manage.py collectstatic --noinput --clear -v 2 && \
python manage.py ensure_superuser && \
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-30} --access-logfile - --error-logfile -"]
