from django.urls import path

from .views import (
    NotificationsAPIView
)

urlpatterns = [
    path('notifications/', NotificationsAPIView.as_view()),
]
