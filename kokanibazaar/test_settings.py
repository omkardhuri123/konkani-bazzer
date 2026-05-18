# ✅ FIXED test_settings.py
# noqa comments tell flake8 to ignore specific rules on specific lines.
# F403 = star import warning, F405 = undefined from star import warning.
# These are acceptable in a test settings file where we intentionally
# inherit all production settings and only override what needs to change.

from .settings import *  # noqa: F403, F405

# Override the database — use SQLite for speed in CI testing.
# No MySQL server needed in GitHub Actions environment.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',  # noqa: F405
    }
}

DEBUG = False
