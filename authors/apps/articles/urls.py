from django.urls import path

from .views import (
    CreateArticleAPIView
)

urlpatterns = [
    path('articles/', CreateArticleAPIView.as_view()),
]
