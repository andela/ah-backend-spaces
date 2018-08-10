from django.urls import path

from .views import ProfileRetrieveAPIView, ProfileFollowingAPIView, RetrieveFollowersAPIView

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveAPIView.as_view()),
    path('profiles/<username>/follow/', ProfileFollowingAPIView.as_view()),
    path('profiles/<username>/followers/', RetrieveFollowersAPIView.as_view())
]
