FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Dépendances système (Pillow + TLS diag)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    ca-certificates curl openssl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt \
 && python -m pip install --upgrade --no-cache-dir certifi

# Variables d'env TLS : forcer l’usage du bundle certifi
ENV SSL_CERT_FILE=/usr/local/lib/python3.12/site-packages/certifi/cacert.pem
ENV AWS_CA_BUNDLE=${SSL_CERT_FILE}
ENV REQUESTS_CA_BUNDLE=${SSL_CERT_FILE}

# Désactiver tout proxy sortant (source fréquente de handshake failure)
ENV HTTP_PROXY=
ENV HTTPS_PROXY=
ENV http_proxy=
ENV https_proxy=
ENV NO_PROXY=*
ENV no_proxy=*

COPY . /app

RUN mkdir -p /app/staticfiles /app/media && \
    adduser --disabled-password --gecos "" django || true && \
    chown -R django:django /app

USER django

EXPOSE 8000

# Démarrage : migrations, check TLS vers R2, collectstatic, superuser, gunicorn
CMD ["bash", "-lc", "\
python - <<'PY'\n\
import certifi, ssl; print('certifi:', certifi.where()); print('OpenSSL:', ssl.OPENSSL_VERSION)\n\
PY\n\
python manage.py migrate --noinput && \
echo '== CLEAR STATICFILES ==' && rm -rf /app/staticfiles/* && \
echo '== CURL R2 HEAD ==' && { [ -n \"$R2_ENDPOINT\" ] && curl -I \"$R2_ENDPOINT\" || true; } && \
echo '== COLLECTSTATIC ==' && python manage.py collectstatic --noinput --clear -v 2 && \
python manage.py ensure_superuser && \
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-30} --access-logfile - --error-logfile -"]
