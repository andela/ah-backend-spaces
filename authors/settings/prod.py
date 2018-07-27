import os
from authors.settings.base import *
from urllib.parse import urlparse

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

db_url = os.getenv("DATABASE_URL")

parsed_url = urlparse(db_url)

dbname = parsed_url.path[1:]
username = parsed_url.username
hostname = parsed_url.hostname
password = parsed_url.password
port = parsed_url.port

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': dbname,
        'USER': username,
        'PASSWORD': password,
        'HOST': hostname,
        'PORT': port,
    }
}
