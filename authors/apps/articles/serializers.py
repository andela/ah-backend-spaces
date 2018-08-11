from django.contrib.auth import authenticate

from rest_framework import serializers

from ..authentication.models import User

from .models import (
    Article, Rating, Comments, ChildComment, ArticleLikes
)
import re


class CreateArticleAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['id', 'title', 'body', 'description',
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


class CommentArticleAPIViewSerializer(serializers.ModelSerializer):

    body = serializers.CharField()
    article_id = Article.pk
    author = User.pk

    class Meta:
        model = Comments
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['body', 'article_id', 'author', 'created_at']

    def validate_body(self, body_var):

        # check if a comment contains more than 8000 characters
        # This includes spaces
        if len(body_var) > 8000:
            raise serializers.ValidationError(
                "A comment cannot be more than 8000 characters including spaces."
            )
        return body_var


class ChildCommentSerializer(serializers.ModelSerializer):
    body = serializers.CharField()
    article_id = Article.pk
    author = User.pk
    parent_id = Comments.pk

    class Meta:
        model = ChildComment
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['body', 'article_id', 'author', 'created_at', 'parent_id']

    def validate_body(self, body_var):

        # check if a comment contains more than 8000 characters
        # This includes spaces
        if len(body_var) > 8000:
            raise serializers.ValidationError(
                "A comment cannot be more than 8000 characters including spaces."
            )
        return body_var


class LikeArticleAPIViewSerializer(serializers.ModelSerializer):

    article_like = serializers.BooleanField()
    user_id = serializers.IntegerField()
    article_id = serializers.IntegerField()

    class Meta:
        model = ArticleLikes
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['article_like', 'user_id', 'article_id']

    def validate_article_id(self, article_id):
        # This method checks if an article with this id exists and raises an
        # error if not.
        article = Article.objects.filter(pk=article_id)

        if not article.exists():
            raise serializers.ValidationError("The article does not exist")
        return article_id

    def verify_article_exists(self, data):
        # This method checks if a like by the same user exists in the system
        # and returns the result accordingly.Its is used by other methods to
        # check for  the same.
        user_id = data.get('user_id', None)
        article_id = data.get('article_id', None)

        likes = ArticleLikes.objects.filter(article_id=article_id,
                                            user_id=user_id
                                            ).values('id',
                                                     'article_like',
                                                     'user_id')
        if likes.exists():
            return True
        return False

    def get_data_items(self, data):
        # This method returns adictioanry of values that will be required by
        # other methods.
        user_id = data.get('user_id', None)
        article_id = data.get('article_id', None)
        article_like = data.get('article_like', None)

        data_items = {
            "article_like": article_like,
            "user_id": user_id,
            "article_id": article_id,
            "status": "like"
        }

        # Swap the like status to `False` if user sent article like `False`
        if article_like is False:
            data_items['status'] = "dislike"

        return data_items

    def perform_save(self, data):
        # This method makes a new entry for the like in the database.If the
        # user has already liked the article they won't like it again.
        if not self.verify_article_exists(data):
            item = self.get_data_items(data)
            like = ArticleLikes(user_id=item['user_id'], article_id=item['article_id'],
                                article_like=item['article_like'])
            like.save()
            return {
                "article_like": like.article_like,
                "user_id": item['user_id'],
                "article_id": item['article_id'],
                "message": 'You have provided a {} for the article'.format(item['status'])
            }
        else:
            raise serializers.ValidationError(
                "You have already provided a like or dislike for this article")

    def perform_update(self, data):
        # This method makes an update on a like that has a user had previously
        # make.It updates the database with the like that is provided.Values
        # donot change if they match the existing.
        if not self.verify_article_exists(data):
            raise serializers.ValidationError(
                "You need to first like or dislike the article")
        else:
            item = self.get_data_items(data)
            like_update = ArticleLikes.objects.filter(article_id=item['article_id'],
                                                      user_id=item['user_id']
                                                      )
            like_update.update(article_like=item['article_like'])
            return {
                "article_like": item['article_like'],
                "user_id": item['user_id'],
                "article_id": item['article_id'],
                "status": "You have updated to {} the article".format(item['status'])
            }

    def perform_delete(self, data):
        # This methods deletes the like from the database when called from the
        # view
        if not self.verify_article_exists(data):
            raise serializers.ValidationError(
                "You cannot delete an article you have not liked or disliked")
        else:
            item = self.get_data_items(data)
            ArticleLikes.objects.filter(article_id=item['article_id'],
                                        user_id=item['user_id']
                                        ).delete()
            return {
                "article_like": None,
                "user_id": item['user_id'],
                "article_id": item['article_id'],
                'status': "Your opinion has been deleted from article likes"
            }
