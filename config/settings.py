# config/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Debug & sécurité de base
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-prod")
DEBUG = os.environ.get("DEBUG", "False") in ("1", "true", "True")

# --- Hôtes & CSRF pilotés par l'env
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "http://localhost,http://127.0.0.1"
    ).split(",")
    if o.strip()
]

# --- Sécurité derrière un proxy TLS (Caddy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "1") in (
    "1",
    "true",
    "True",
)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "ckeditor",
    "ckeditor_uploader",
    "sitecontent",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sitecontent.context_processors.site_contact",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de données (Postgres en prod, SQLite sinon)
if os.environ.get("DB_ENGINE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "annoor"),
            "USER": os.environ.get("DB_USER", "annoor"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "db"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- i18n
LANGUAGE_CODE = "fr"
LANGUAGES = [("fr", "Français"), ("en", "English")]
TIME_ZONE = "Africa/Niamey"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Static & media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"  # ← ajouté
)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Email
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "contact@annoor.tech")

# --- CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 360,
        "width": "100%",
        "extraPlugins": ",".join(["uploadimage"]),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
