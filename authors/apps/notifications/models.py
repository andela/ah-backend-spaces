from django.db import models
from ..authentication.models import User
from ..articles.models import Article

# Create your models here.


class Notifications(models.Model):
    # this field holds the article id of the notification
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)

    # this holds the title of the notification
    notification_title = models.CharField(db_index=True, max_length=255)

    # this hold the body of the notification
    notification_body = models.CharField(db_index=True, max_length=255)

    # this holds the id of the person this notification is for
    notification_owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # marks a notification as read or not read
    read_status = models.BooleanField(db_index=True, default=False)

    # time stamp of when the notification was created
    created_at = models.DateTimeField(auto_now_add=True)

    # time stamp of when the was read or unread
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
