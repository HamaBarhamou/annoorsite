# config/settings.py
import os, sys
from pathlib import Path
import dj_database_url
from django.utils.module_loading import import_string

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# Débogage & clé secrète
# -------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-prod")
IS_RUNSERVER = "runserver" in sys.argv
DEBUG = os.environ.get("DEBUG", "False") in ("1", "true", "True")

# -------------------------------------------------------------------
# Hôtes & CSRF (pilotés par variables d'env)
# NB: mettre les domaines réels en prod, avec schéma https:// pour CSRF
# -------------------------------------------------------------------
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

# Derrière un proxy TLS (Caddy/Nginx/…)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

""" if DEBUG:
    SECURE_SSL_REDIRECT = False
else:
    SECURE_SSL_REDIRECT = True """

# SSL redirect: jamais en runserver; en prod sinon
SECURE_SSL_REDIRECT = os.environ.get(
    "SECURE_SSL_REDIRECT", "0" if IS_RUNSERVER or DEBUG else "1"
) in ("1", "true", "True")

print("DEBGUG=", DEBUG)

# Cookies sécurisés selon DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# -------------------------------------------------------------------
# Apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # 3rd-party
    "ckeditor",
    "ckeditor_uploader",
    # Project apps
    "sitecontent",
]

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # doit être haut dans la pile
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Base de données : Postgres en prod (via variables), sinon SQLite
# -------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Exemple Render : postgres://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "60")),
            ssl_require=True,  # force SSL si le provider ne met pas ?sslmode=require
        )
    }
elif os.environ.get("DB_ENGINE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "annoor"),
            "USER": os.environ.get("DB_USER", "annoor"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "db"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
            "OPTIONS": {"sslmode": os.environ.get("DB_SSLMODE", "require")},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -------------------------------------------------------------------
# i18n / TZ
# -------------------------------------------------------------------
LANGUAGE_CODE = "fr"
LANGUAGES = [("fr", "Français"), ("en", "English")]
TIME_ZONE = "Africa/Niamey"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# -------------------------------------------------------------------
# Static & Media
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise uniquement via STORAGES (pas de STATICFILES_STORAGE global)
STORAGES = {
    # stockage par défaut des médias (filesystem local tant que USE_R2_MEDIA=0)
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # fichiers statiques : simple en dev, Manifest en prod
    "staticfiles": (
        {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
        if DEBUG
        else {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
    ),
}

# En Manifest, si une entrée manque, WhiteNoise ne crashe pas (utile le temps de corriger)
WHITENOISE_MANIFEST_STRICT = False

# --- MEDIA local par défaut ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Choix du backend médias (Cloudflare R2/S3) ---
# --- R2 (S3-compatible) ---
USE_R2_MEDIA = os.environ.get("USE_R2_MEDIA", "0") in ("1", "true", "True")
if USE_R2_MEDIA:
    INSTALLED_APPS += ["storages"]

    AWS_S3_ENDPOINT_URL = os.environ.get("R2_ENDPOINT")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")

    AWS_S3_REGION_NAME = "auto"
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    # IMPORTANT : évite le sous-domaine <bucket>.<account>.r2... → pas de souci TLS
    AWS_S3_ADDRESSING_STYLE = "path"

    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False

    # URL publique (cdn/r2.dev/sous-domaine media)
    R2_PUBLIC_BASE_URL = os.environ.get("R2_PUBLIC_BASE_URL", "").rstrip("/")
    if R2_PUBLIC_BASE_URL:
        MEDIA_URL = f"{R2_PUBLIC_BASE_URL}/"
    elif AWS_S3_ENDPOINT_URL and "://" in AWS_S3_ENDPOINT_URL:
        # fallback public (peu utile sans ACL public)
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"

    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# -------------------------------------------------------------------
# Email
# -------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "contact@annoor.tech")

# -------------------------------------------------------------------
# CKEditor
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Logging minimal (stdout) + admins
# -------------------------------------------------------------------
import logging  # noqa: E402

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

ADMINS = [("Admin", os.environ.get("ADMIN_EMAIL", "admin@annoor.tech"))]
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "django@annoor.tech")

# -------------------------------------------------------------------
# Durcissement HTTPS additionnel en prod
# -------------------------------------------------------------------
if not DEBUG:
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = os.environ.get("SECURE_REFERRER_POLICY", "same-origin")
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -------------------------------------------------------------------
# Email (Namecheap PrivateEmail) — sécurisé & piloté par env
# -------------------------------------------------------------------

EMAIL_HOST = os.environ.get("EMAIL_HOST", "mail.privateemail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "465"))  # 465=SSL direct ; 587=STARTTLS
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "contact@annoor.tech")
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD"
)  # *** via variable d'env ***
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "20"))

# Choix SSL/TLS via env pour flexibilité
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "1") in ("1", "true", "True")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "0") in ("1", "true", "True")

# Fallback backend: si pas d'identifiants → console en dev/runserver
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    # En dev sans secrets => pas d'erreur, on loggue dans la console
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", EMAIL_HOST_USER)
CONTACT_INBOX = os.environ.get("CONTACT_INBOX", EMAIL_HOST_USER)
