from datetime import datetime, timedelta
from ..authentication.models import User

from django.db import models


class Article(models.Model):

    # title is the article titlie to be published
    title = models.CharField(db_index=True, max_length=255)

    # body contains the information an author is trying to put across
    body = models.TextField(db_index=True)

    # description contains what the publication is all about
    description = models.CharField(db_index=True, max_length=255)

    # this field makes a publication searchable
    # it is got off a title but should never be the same
    slug = models.SlugField(db_index=True, max_length=255, unique=True)

    # this makes the publication viewable by all audiences
    published = models.BooleanField(default=False)

    # this takes the time stamp of when the article was made
    created_at = models.DateTimeField(auto_now_add=True)

    # This takes the time stamp of when the article was published
    updated_at = models.DateTimeField(auto_now=True)

    # This makes identifies the owner of the publication
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
