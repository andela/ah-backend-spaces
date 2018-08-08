from django.urls import path

from .views import (
    CreateArticleAPIView, RateArticleAPIView
)

urlpatterns = [
    path('articles/', CreateArticleAPIView.as_view()),
    path('articles/rate/<int:article_id>', RateArticleAPIView.as_view()),
]
