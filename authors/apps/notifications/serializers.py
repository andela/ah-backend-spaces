from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import (
    Notifications
)


class NotificationsAPIViewSerializer(serializers.Serializer):
    notifications = serializers.ListField()
    user_id = serializers.IntegerField()

    def validate(self, data):
        notifications = data.get('notifications', None)
        user_id = data.get('user_id', None)

        # get all notifications beloging to that user
        db_notifications = Notifications.objects.filter(
            notification_owner=user_id, read_status=False).values("id")
        list_of_notifications = [
            notification["id"] for notification in db_notifications
        ]

        comparison = [i for i in list_of_notifications if i in notifications]

        non_existent_ids = [i for i in notifications if i not in comparison]

        if len(comparison) < len(notifications):
            raise serializers.ValidationError(
                "The " + str(non_existent_ids) + " Id(s) do to exist.")
        return data

    def update_read_status(self, notification_id_list):
        for _ in notification_id_list:
            instance = Notifications.objects.get(pk=_)
            setattr(instance, "read_status", True)
            instance.save()


class GetNotificationsAPIViewSerializer(serializers.ModelSerializer):
    notification_owner = Notifications.pk

    class Meta:
        model = Notifications
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['notification_owner', 'read_status']

    def validate(self, data):
        return data
