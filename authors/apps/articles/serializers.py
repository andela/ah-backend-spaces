from django.contrib.auth import authenticate

from rest_framework import serializers

from ..authentication.models import User

from .models import Article, Rating

import re


class CreateArticleAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['title', 'body', 'description',
                  'user_id', 'slug', 'published', 'created_at']


class RatingArticleAPIViewSerializer(serializers.ModelSerializer):

    rating = serializers.CharField()
    article_id = Article.pk
    user_id = User.pk

    class Meta:
        model = Rating
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['rating', 'review', 'article_id', 'user_id']

    def validate_rating(self, rating_var):
        if not re.match("[1-5]", rating_var):
            raise serializers.ValidationError(
                "Rating should be in range of 1 to 5."
            )
        return rating_var

    def validate(self, data):
        user_id = data.get('user_id', None)
        article_id = data.get('article_id', None)

        # get user id of author of article
        user_to_rate = article_id.user_id

        if user_to_rate == user_id:
            raise serializers.ValidationError(
                "You cannot rate your own article"
            )

        # check if user has rated that article before
        db_rating = Rating.objects.filter(
            article_id=article_id.pk, user_id=user_id)
        if db_rating.exists():
            raise serializers.ValidationError(
                "You cannot rate an article twice."
            )
        return data
