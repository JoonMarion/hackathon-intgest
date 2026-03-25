from .base import *  # noqa: F403
from decouple import Csv, config

DEBUG = False

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
