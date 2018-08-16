from django.contrib.auth import authenticate

from rest_framework import serializers

from ..authentication.models import User

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from .models import (
    Article, Rating, Comments, ChildComment, ArticleLikes,
    ArticleFavourites as ArticleFs
)
from ..notifications.models import Notifications
from ..profiles.models import Profile
import re
from authors.apps.profiles.serializers import ProfileSerializer


class CreateArticleAPIViewSerializer(TaggitSerializer, serializers.ModelSerializer):

    tags = TagListSerializerField(required=False)
    author = serializers.SerializerMethodField()
    user_id = User.pk

    def get_author(self, article):
        user = {
            "username": article.author.username,
            "bio": article.author.profile.bio,
            "image": article.author.profile.image
        }

        return user

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['id', 'title', 'body', 'description',
                  'author', 'slug', 'published', 'created_at', 'tags']

    def validate_title(self, title_var):
        if len(title_var) > 150:
            raise serializers.ValidationError(
                "Title cannot be greater than 150 characters."
            )
        return title_var

    def validate_description(self, description_var):
        if len(description_var) > 600:
            raise serializers.ValidationError(
                "Description cannot be greater than 150 characters."
            )
        return description_var


class UpdateArticleAPIViewSerializer(serializers.ModelSerializer):
    user_id = User.pk

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['id', 'title', 'body', 'description',
                  'author', 'slug', 'published', 'created_at', 'tags']

    def validate_title(self, title_var):
        if len(title_var) > 150:
            raise serializers.ValidationError(
                "Title cannot be greater than 150 characters."
            )
        return title_var

    def validate_description(self, description_var):
        if len(description_var) > 600:
            raise serializers.ValidationError(
                "Description cannot be greater than 150 characters."
            )
        return description_var

    def update_article(self, article_id, data, user_id):
        try:
            article_instance = Article.objects.get(pk=article_id)
        except:  # noqa: E722
            raise serializers.ValidationError(
                "Article with id " + str(article_id) + " was not found."
            )

        # get username using userid
        # this helps us call the notifications class method that
        # will generate notifications of a published article to a user's following
        username = User.objects.filter(pk=user_id).values("username")[
            0]["username"]

        if article_instance.title == data["title"]:
            data.pop("slug", None)

        user_followers = []

        if article_instance.published is False and \
                data["published"]:
            user_followers = self.notifications(username, article_id)
            for follower_id in user_followers:
                Notifications.objects.create(article_id=Article.objects.get(
                    pk=article_id), notification_title=article_instance.title,
                    notification_body=article_instance.body,
                    notification_owner=User.objects.get(pk=follower_id))

        for (key, value) in data.items():
            setattr(article_instance, key, value)
        article_instance.save()

        return len(user_followers)

    def notifications(self, username, followee_id):
        list_of_followers = []

        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except:  # noqa: E722
            pass

        user_followers = Profile.follows.through.objects.filter(
            to_profile_id=profile.id)
        for a_follower in user_followers:
            list_of_followers.append(
                str(a_follower.from_profile_id)
            )

        # store notifications in the notifications database

        return list_of_followers


class RatingArticleAPIViewSerializer(serializers.ModelSerializer):

    rating = serializers.CharField()
    article_id = Article.pk
    user_id = User.pk

    class Meta:
        model = Rating
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['rating', 'review', 'article_id', 'author']

    def validate_rating(self, rating_var):
        if not re.match("[1-5]", rating_var):
            raise serializers.ValidationError(
                "Rating should be in range of 1 to 5."
            )
        return rating_var

    def validate(self, data):
        user_id = data.get('author', None)
        article_id = data.get('article_id', None)

        # get user id of author of article
        user_to_rate = article_id.author

        if user_to_rate == user_id:
            raise serializers.ValidationError(
                "You cannot rate your own article"
            )

        # check if user has rated that article before
        db_rating = Rating.objects.filter(
            article_id=article_id.pk, author_id=user_id)
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
        fields = ['id', 'body', 'article_id', 'author', 'created_at']

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
        fields = ['id', 'body', 'article_id',
                  'author', 'created_at', 'parent_id']

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
    author = serializers.IntegerField()
    article_id = serializers.IntegerField()

    class Meta:
        model = ArticleLikes
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['article_like', 'author', 'article_id']

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
        author = data.get('author', None)
        article_id = data.get('article_id', None)

        likes = ArticleLikes.objects.filter(article_id=article_id,
                                            author_id=author
                                            ).values('id',
                                                     'article_like',
                                                     'author_id')
        if likes.exists():
            return True
        return False

    def get_data_items(self, data):
        # This method returns adictioanry of values that will be required by
        # other methods.
        author = data.get('author', None)
        article_id = data.get('article_id', None)
        article_like = data.get('article_like', None)

        data_items = {
            "article_like": article_like,
            "author": author,
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
            like = ArticleLikes(author_id=item['author'], article_id=item['article_id'],
                                article_like=item['article_like'])
            like.save()
            return {
                "article_like": like.article_like,
                "author": item['author'],
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
                                                      author_id=item['author']
                                                      )
            like_update.update(article_like=item['article_like'])
            return {
                "article_like": item['article_like'],
                "author": item['author'],
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
                                        author_id=item['author']
                                        ).delete()
            return {
                "article_like": None,
                "author": item['author'],
                "article_id": item['article_id'],
                'status': "Your opinion has been deleted from article likes"
            }


class FavouriteArticleAPIViewSerializer(serializers.ModelSerializer):

    article_favourite = serializers.BooleanField()
    author = serializers.IntegerField()
    article_id = serializers.IntegerField()

    class Meta:
        model = ArticleFs
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['article_favourite', 'author', 'article_id']

    def validate_article_id(self, article_id):
        # This method checks if an article with this id exists and raises an
        # error if not.
        article = Article.objects.filter(pk=article_id)

        if not article.exists():
            raise serializers.ValidationError("The article does not exist")
        return article_id

    def verify_article_exists(self, data):
        # This method checks if an article has already been favourited by the
        # same user and return the result accordingly. Its is used by other
        # methods to check for  the same.
        author = data.get('author', None)
        article_id = data.get('article_id', None)

        likes = ArticleFs.objects.filter(article_id=article_id,
                                         author_id=author
                                         ).values('id',
                                                  'article_favourite',
                                                  'author_id')
        if likes.exists():
            return True
        return False

    def get_data_items(self, data):
        # This method returns adictioanry of values that will be required by
        # other methods.
        author = data.get('author', None)
        article_id = data.get('article_id', None)
        article_favourite = data.get('article_favourite', None)

        data_items = {
            "article_favourite": article_favourite,
            "author": author,
            "article_id": article_id,
            "status": "article added to "
        }

        # Swap the like status to `False` if user sent article like `False`
        if article_favourite is False:
            data_items['status'] = "article removed from "

        return data_items

    def perform_save(self, data):
        # This method makes a new entry for the like in the database.If the
        # user has already liked the article they won't like it again.

        item = self.get_data_items(data)
        if item['article_favourite'] is False:
            raise serializers.ValidationError(
                "Use true to add article to your list of favourite articles")
        elif self.verify_article_exists(data):
            raise serializers.ValidationError(
                "You have already added this article in your favourites list")
        else:
            like = ArticleFs(author_id=item['author'],
                             article_id=item['article_id'],
                             article_favourite=item['article_favourite'])
            like.save()
            return {
                "article_favourite": like.article_favourite,
                "author": item['author'],
                "article_id": item['article_id'],
                "message": "{} your list of favourite articles".format(
                    item['status'])
            }

    def perform_delete(self, data):
        # This methods deletes the like from the database when called from the
        # view

        item = self.get_data_items(data)
        if not self.verify_article_exists(data):
            raise serializers.ValidationError(
                "Article already removed from your favourites list")
        elif item['article_favourite'] is True:
            raise serializers.ValidationError(
                "Use false to remove article from your favourites list")
        else:
            ArticleFs.objects.filter(article_id=item['article_id'],
                                     author_id=item['author']
                                     ).delete()
            return {
                "message": "article removed from your list favourites articles"
            }
