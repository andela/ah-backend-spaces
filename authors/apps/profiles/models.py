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

    # number of poeple folliwing this profile
    followers = models.IntegerField(default=0)

    # number of people this profile follows
    following = models.IntegerField(default=0)

    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        """ function for following a profile """
        self.follows.add(profile)

    def unfollow(self, profile):
        """ function for unfollowing a profile"""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Check if a user is already following the profile"""
        return self.follows.filter(pk=profile.pk).exists()
