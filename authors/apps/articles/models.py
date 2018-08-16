from datetime import datetime, timedelta
from ..authentication.models import User

from django.db import models
from taggit.managers import TaggableManager


class Article(models.Model):

    # title is the article titlie to be published
    title = models.CharField(db_index=True, max_length=255)

    # body contains the information an author is trying to put across
    body = models.TextField(db_index=True)

    # description contains what the publication is all about
    description = models.CharField(db_index=True, max_length=255)

    # this field makes a publication searchable
    # it is got off a title but should never be the same
    slug = models.SlugField(db_index=True, max_length=255, unique=True)

    # this makes the publication viewable by all audiences
    published = models.BooleanField(default=False)

    # this takes the time stamp of when the article was made
    created_at = models.DateTimeField(auto_now_add=True)

    # This takes the time stamp of when the article was updated
    updated_at = models.DateTimeField(auto_now=True)

    # This makes identifies the owner of the publication
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # tage_field = models.ManyToManyField()
    tags = TaggableManager(blank=True)

    objects = models.Manager()


class Rating(models.Model):

    # this contains the rating level a given to an article
    rating = models.IntegerField(db_index=True)

    # This contains the message given based on a user insight
    #  of an article on review, it can be left empty and is optional
    review = models.CharField(
        db_index=True, max_length=255, null=True, blank=True)

    # this field enables us identify which review belongs to which article
    # it is a foreign key from articles
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)

    # this enables us know which user rated the article
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # this takes the time stamp of when an article was rated
    created_at = models.DateTimeField(auto_now_add=True)

    # This takes the time stamp of when the article's rating was updated
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class Comments(models.Model):

    # this contains the comment text to an article
    body = models.CharField(db_index=True, max_length=255)

    # this field enables us identify which comment belongs to which article
    # it is a foreign key from articles
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)

    # this enables us know which user commented on an article
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # this takes the time stamp of when an article was commented on
    created_at = models.DateTimeField(auto_now_add=True)

    # This takes the time stamp of when the article's comment was updated
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class ChildComment(models.Model):

    # this contains the comment text to an article
    body = models.CharField(db_index=True, max_length=255)

    # this field enables us identify which comment belongs to which article
    # it is a foreign key from articles
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)

    # conatins the id if the parent comment that one is reacting to
    parent_id = models.ForeignKey(Comments, on_delete=models.CASCADE)

    # this enables us know which user commented on an article
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # this takes the time stamp of when an article was commented on
    created_at = models.DateTimeField(auto_now_add=True)

    # This takes the time stamp of when the article's comment was updated
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class ArticleLikes(models.Model):

    # id of the article to be created
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True)

    # this takes the value of the like by a user
    article_like = models.BooleanField(db_index=True, default=None)

    # this takes in th user id of the user who has liked
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # time stamp of when the article was first liked at
    article_liked_at = models.DateTimeField(auto_now_add=True)

    # time stamp of when the article was last liked or unliked
    like_updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class ArticleFavourites(models.Model):

    # id of the article to be favourited
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True)

    # this takes the value of the favourite by a user
    article_favourite = models.BooleanField(db_index=True, default=None)

    # this takes in th user id of the user who has favourited the article
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # time stamp of when the article was favourited at
    article_favourited_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
