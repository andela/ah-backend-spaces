from django.urls import path

from .views import ProfileRetrieveAPIView

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveAPIView.as_view())
]
