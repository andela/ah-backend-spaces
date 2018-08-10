from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView, CreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..authentication.backends import JWTAuthentication
from ..authentication.models import User
from .models import Notifications

from .renderers import (
    NotificationsJSONRenderer
)

from .serializers import (
    NotificationsAPIViewSerializer, GetNotificationsAPIViewSerializer
)


class NotificationsAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (NotificationsJSONRenderer,)

    def put(self, request):
        """
        This class method is used to update a users article
        """
        serializer_class = NotificationsAPIViewSerializer

        notification = request.data.get('notification', {})

        user_data = JWTAuthentication().authenticate(request)

        # append user_id from token to article variable for later validations in serializers
        notification["user_id"] = user_data[1]

        serializer = serializer_class(data=notification)
        serializer.is_valid(raise_exception=True)

        # update the notification statue to True
        serializer.update_read_status(serializer.data["notifications"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        retrieve all notifications of a user
        """
        # decode users authentication token
        user_data = JWTAuthentication().authenticate(request)

        # get user notifications details from the Notifications table in the database
        notifications = Notifications.objects.filter(notification_owner=user_data[1]).values(
            "id", "article_id", "notification_title", "notification_body",
            "notification_owner", "read_status"
        )

        # create a list of notifications
        # the action below is done by use of list comprehension
        list_of_notifications = [i for i in notifications]

        return Response({"notifications": list_of_notifications}, status=status.HTTP_200_OK)
