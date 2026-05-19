import environ
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)  # type: ignore

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
# DB_ENGINE in your .env file controls which database backend to use.
# Local development (Windows + MySQL): DB_ENGINE=django.db.backends.mysql
# PythonAnywhere free tier (SQLite):   DB_ENGINE=django.db.backends.sqlite3

DB_ENGINE = env("DB_ENGINE", default="django.db.backends.sqlite3")  # type: ignore

if DB_ENGINE == "django.db.backends.sqlite3":
    # SQLite is a simple file-based database. No server, no credentials needed.
    # The database lives at BASE_DIR/db.sqlite3 — a single file in your project.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # MySQL configuration — used in local development on Windows.
    # All credentials come from the .env file, never hardcoded here.
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST", default="localhost"),  # type: ignore
            "PORT": env("DB_PORT", default="3306"),  # type: ignore
            "TIME_ZONE": "Asia/Kolkata",
            "OPTIONS": {
                "charset": "utf8mb4",
                "auth_plugin_map": "mysql_native_password",
                "init_command": "SET time_zone = '+05:30'",
            },
        }
    }


# --- Static & Media Files ---
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
# ✅ CORRECT — puts media/ at the project root alongside manage.py
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Security (Recommended)
SECURE_SSL_REDIRECT = False  # Keep False on free plan
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
