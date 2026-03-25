from .base import *  # noqa: F403
from decouple import Csv, config

DEBUG = False
SECRET_KEY = config("SECRET_KEY", default="test-secret-key")
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="testserver,localhost,127.0.0.1",
    cast=Csv(),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
