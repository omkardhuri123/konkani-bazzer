# This file is ONLY used during CI testing on GitHub Actions.
# It overrides the database setting to use SQLite so we don't
# need a real MySQL server running during tests.

from .settings import *   # Import everything from real settings

# Override the database — use SQLite for speed in testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Disable debug for realistic test conditions
DEBUG = False