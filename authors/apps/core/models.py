from django.db import models


class TimestampedModel(models.Model):
    """
    Abstracting common user and profile model fields
    """
    # a timestamp of when an object inheriting from this class was created
    created_at = models.DateTimeField(auto_now_add=True)

    # a timestamp of when an object inheriting from this class was updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # ordering for models
        ordering = ['-created_at', '-updated_at']
