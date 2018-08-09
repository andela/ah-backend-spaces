from django.urls import path

from .views import (
    CreateArticleAPIView, RateArticleAPIView, CommentArticleAPIView
)

urlpatterns = [
    path('articles/', CreateArticleAPIView.as_view()),
    path('articles/rate/<int:article_id>', RateArticleAPIView.as_view()),
    path('articles/<int:article_id>/comment/', CommentArticleAPIView.as_view()),
]
