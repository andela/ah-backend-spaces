import os
from authors.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG_MODE')

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# using the dj_database_url python package
# https://stackoverflow.com/questions/16868451/how-to-set-up-database-for-django-app-on-heroku
# https://devcenter.heroku.com/articles/python-concurrency-and-database-connections
# https://stackoverflow.com/questions/27985368/heroku-databases-is-not-defined
DATABASES = {'default': dj_database_url.config(
    conn_max_age=600, ssl_require=True)}
