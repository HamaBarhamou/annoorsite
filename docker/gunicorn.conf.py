# docker/gunicorn.conf.py
import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get("GUNICORN_THREADS", 2))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL", 30))
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
