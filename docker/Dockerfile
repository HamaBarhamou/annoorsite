# docker/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (psycopg2 build & Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Requirements en amont pour profiter du cache Docker
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copie du projet
COPY . /app

# Répertoires de volumes (static & media)
RUN mkdir -p /vol/static /vol/media && \
    adduser --disabled-password --gecos "" django && \
    chown -R django:django /vol && chmod -R 755 /vol

USER django

# Entrée
CMD ["bash", "docker/entrypoint.sh"]
