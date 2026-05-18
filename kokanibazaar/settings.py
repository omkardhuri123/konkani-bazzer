import environ
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # type: ignore[arg-type]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"] if DEBUG else []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
    "widget_tweaks",
]

AUTH_USER_MODEL = "store.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kokanibazaar.urls"
WSGI_APPLICATION = "kokanibazaar.wsgi.application"
ASGI_APPLICATION = "kokanibazaar.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.cart",
            ],
        },
    },
]

# --- Database Configuration ---
# MySQL is used in all environments. Credentials always come from .env.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),  # type: ignore[arg-type]
        "PORT": env("DB_PORT", default="3306"),  # type: ignore[arg-type]
        # KEY FIX: Tell Django the database connection runs in IST using a
        # numeric offset (+05:30) instead of the IANA name 'Asia/Kolkata'.
        # MySQL can resolve numeric offsets natively without needing its
        # timezone lookup tables installed — which are empty on Windows by default.
        "TIME_ZONE": "Asia/Kolkata",
        "OPTIONS": {
            "charset": "utf8mb4",
            "auth_plugin_map": "mysql_native_password",
            # This sets the MySQL session timezone to +05:30 (IST) using a
            # numeric offset. Django's CONVERT_TZ() calls will use this offset
            # instead of the string 'Asia/Kolkata', bypassing the need for
            # MySQL timezone tables entirely.
            "init_command": "SET time_zone = '+05:30'",
        },
    }
}

# --- Static & Media Files ---
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
# ✅ CORRECT — puts media/ at the project root alongside manage.py
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security (Recommended)
SECURE_SSL_REDIRECT = False   # Keep False on free plan
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# --- Auth Redirects ---
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- Localisation ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging ---
# ✅ Add this line just ABOVE your LOGGING = { ... } block
# This ensures the logs/ directory exists before the logging system tries to write to it
(BASE_DIR / "logs").mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s:%(lineno)d %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "logs" / "django.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
        "django.request": {"handlers": ["file"], "level": "ERROR", "propagate": False},
        "django.server": {"handlers": ["file"], "level": "ERROR", "propagate": False},
        "store": {"handlers": ["file"], "level": "DEBUG", "propagate": True},
    },
}
