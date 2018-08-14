from django.urls import path

from .views import (
    CreateArticleAPIView, RateArticleAPIView, CommentArticleAPIView,
    LikeArticleAPIView, FavouriteArticleAPIView
)

urlpatterns = [
    path('articles/', CreateArticleAPIView.as_view()),
    path('articles/<int:article_id>/comment/', CommentArticleAPIView.as_view()),
    path('articles/<int:article_id>/rating/', RateArticleAPIView.as_view()),
    path('articles/<int:article_id>/', LikeArticleAPIView.as_view()),
    path('articles/<int:article_id>/favourite/', FavouriteArticleAPIView.as_view()),
]
