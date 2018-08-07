from django.db import models
from authors.apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    """
    Profile that has user's profile fields
    """

    # tying a single user to a profile
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )

    # field to store and display some info about a user
    bio = models.TextField(blank=True)

    # a user may have an optional profile image
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
