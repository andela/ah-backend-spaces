from rest_framework import status, exceptions
from rest_framework.generics import (RetrieveAPIView,
                                     RetrieveUpdateAPIView, CreateAPIView,
                                     RetrieveUpdateDestroyAPIView, ListAPIView
                                     )
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.template.defaultfilters import slugify
import uuid
from ..authentication.backends import JWTAuthentication
from ..authentication.models import User
from . models import Rating as DbRating, Article
from .exceptions import NoResultsMatch

from .exceptions import ArticlesNotExist
from .renderers import (
    ArticlesJSONRenderer, CommentJSONRenderer, RatingJSONRenderer,
    ListArticlesJSONRenderer
)

from .serializers import (
    CreateArticleAPIViewSerializer, RatingArticleAPIViewSerializer,
    CommentArticleAPIViewSerializer, ChildCommentSerializer,
    LikeArticleAPIViewSerializer, FavouriteArticleAPIViewSerializer,
    UpdateArticleAPIViewSerializer
)
import re


class CreateArticleAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticlesJSONRenderer,)
    serializer_class = CreateArticleAPIViewSerializer

    def post(self, request):
        """
        This class method is used to create user articles
        """
        article = request.data.get('article', {})

        # decode user token and return its value
        user_data = JWTAuthentication().authenticate(request)

        article["author"] = user_data[1]

        # create a an article slug fron title
        try:
            slug = slugify(article["title"]).replace("_", "-")
            slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
            article["slug"] = slug
        except KeyError:
            pass

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user_data[0])
        data = serializer.data
        data["message"] = "Article created successfully."

        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, article_id):
        serializer_class = UpdateArticleAPIViewSerializer
        """
        This class method is used to update a users article
        """
        article = request.data.get('article', {})

        # decode user token and return its value
        user_data = JWTAuthentication().authenticate(request)

        # append user_id from token to article variable for later validations in serializers
        article["author"] = user_data[1]

        article['aid'] = article_id

        # create a an article slug fron title
        try:
            slug = slugify(article["title"]).replace("_", "-")
            slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
            article["slug"] = slug
        except KeyError:
            pass

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = serializer_class(data=article)
        serializer.is_valid(raise_exception=True)

        # create an instance of user model class from user id
        # gotten from the token paresd to the route token
        article["author"] = User.objects.get(pk=user_data[1])

        # call the update_article class method in serializers
        # this updates the article content but also does a couple of validations
        serializer.update_article(article_id, article, user_data[1])

        # create a data variable that contains all data to be sent back on success
        data = serializer.data
        data["message"] = "Article updated successfully."

        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request, article_id):
        """
        This class method is used to fetch a users article by id
        """

        # create an instance of article model class from article id
        # gotten from the url paresd.
        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            return Response({"error": "This article doesnot exist"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(article)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, article_id):
        """
        This class method is used to fetch a users article by id
        """

        user_data = JWTAuthentication().authenticate(request)
        # create an instance of article model class from article id
        # gotten from the url paresd.
        try:
            article = Article.objects.get(pk=article_id,
                                          author_id=user_data[0].id)
        except Article.DoesNotExist:
            return Response({"error": "This article doesnot exist"},
                            status=status.HTTP_404_NOT_FOUND)

        article.delete()

        return Response({"message": "article was deleted successully"}, status=status.HTTP_200_OK)


class ListAuthArticlesAPIView(ListAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ListArticlesJSONRenderer,)
    serializer_class = CreateArticleAPIViewSerializer

    def get_queryset(self):

        user_data = JWTAuthentication().authenticate(self.request)
        articles = Article.objects.filter(author=user_data[0].id,)
        if len(articles) == 0:
            raise ArticlesNotExist
        return articles


class ListArticlesAPIView(ListAPIView):

    permission_classes = (AllowAny,)
    renderer_classes = (ListArticlesJSONRenderer,)
    serializer_class = CreateArticleAPIViewSerializer

    def get_queryset(self):

        articles = Article.objects.filter(published=True)

        if len(articles) == 0:
            raise ArticlesNotExist
        return articles


class ListArticleAPIView(RetrieveAPIView):

    permission_classes = (AllowAny,)
    renderer_classes = (ListArticlesJSONRenderer,)
    serializer_class = CreateArticleAPIViewSerializer

    def get(self, request, article_id):

        # create an instance of article model class from article id
        # gotten from the url paresd.
        try:
            article = Article.objects.get(pk=article_id, published=True)
        except Article.DoesNotExist:
            return Response({"error": "This article doesnot exist"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(article)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RateArticleAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (RatingJSONRenderer,)
    serializer_class = RatingArticleAPIViewSerializer

    def post(self, request, article_id):
        Rating = request.data.get('rating', {})

        # Add the article id to rating to be made
        Rating["article_id"] = article_id

        # decode user token and return its value
        user_data = JWTAuthentication().authenticate(request)

        # get id of the user rating an article
        Rating["author"] = user_data[1]

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = self.serializer_class(data=Rating)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data["message"] = "Article rated successfully."

        # get all user ratings from the database
        rating_data = DbRating.objects.filter(
            article_id=article_id).values('rating')

        # generate a list of all rating on an article using list comprehension
        list_of_ratings = [rating["rating"] for rating in rating_data]

        # callculate average rating by dividing sum over number of items in the list
        average_rating = sum(list_of_ratings) / len(list_of_ratings)

        # append the rating to data being output
        data["average_rating"] = average_rating

        # append success message to output
        data["message"] = "Article rated successfully."

        # append the number of people who rated the article to the output
        data["no_of_ratings"] = len(list_of_ratings)

        return Response(data, status=status.HTTP_201_CREATED)


class CommentArticleAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)

    # serailizer class to be used for parent comment
    # A parent comment is a comment that can have threaded comments attached to it
    serializer_class_a = CommentArticleAPIViewSerializer

    # serializer class to be used for child comment
    # A child comment is a thread to a main comment
    serializer_class_b = ChildCommentSerializer

    def post(self, request, article_id):
        comment = request.data.get('comment', {})

        try:
            # check if a parent id is suplied
            # if supplied add the parent id to comment that
            # is supposed to be verified and change seralizer class method
            comment["parent_id"] = comment["parent_id"]
            serializer_class = self.serializer_class_b
        except KeyError:
            # if no comment parent id is supplied, use the below serializer class instance
            serializer_class = self.serializer_class_a

        # Add the article id to rating to be made
        comment["article_id"] = article_id

        # decode user token and return its value
        user_data = JWTAuthentication().authenticate(request)

        # get id of the user rating an article
        comment["author"] = user_data[1]

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = serializer_class(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data["message"] = "Comment created successfully."

        return Response(data, status=status.HTTP_201_CREATED)


class LikeArticleAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticlesJSONRenderer,)
    serializer_class = LikeArticleAPIViewSerializer

    def get(self, request, article_id):

        return Response({"error": "method GET not allowed"},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, article_id):
        """ This function is handling requests for creating a like

        Args:
            request: contains more details about the request made
            article_id: id of the article to be liked

        Return: Response showing that the article was liked
        """

        like = request.data.get('article', {})

        user_data = JWTAuthentication().authenticate(request)

        like["author"] = user_data[1]

        like["article_id"] = article_id

        serializer = self.serializer_class(data=like)
        serializer.is_valid(raise_exception=True)

        result = serializer.perform_save(like)

        return Response(result)

    def put(self, request, article_id):
        """ This function is handling requests for updating a like

        Args:
            request: contains more details about the request made
            article_id: id of the article to check for when updating

        Return: Response showing that the article was updated
        """
        like = request.data.get('article', {})

        user_data = JWTAuthentication().authenticate(request)

        like["author"] = user_data[1]

        like["article_id"] = article_id

        serializer = self.serializer_class(data=like)
        serializer.is_valid(raise_exception=True)

        result = serializer.perform_update(like)

        return Response(result)

    def delete(self, request, article_id):
        """ This function is handling requests for deleting a like

        Args:
            request: contains more details about the request made
            article_id: id of the article to be deleted

        Return: Response showing that the article was deleted
        """
        serializer_data = request.data.get('article', {})

        user_data = JWTAuthentication().authenticate(request)

        serializer_data["author"] = user_data[1]
        serializer_data["article_id"] = article_id

        serializer = self.serializer_class(
            data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)

        result = serializer.perform_delete(serializer_data)

        return Response(result, status=status.HTTP_200_OK)


class FavouriteArticleAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticlesJSONRenderer,)
    serializer_class = FavouriteArticleAPIViewSerializer

    def post(self, request, article_id):
        """ This function is handling requests for creating a like

        Args:
            request: contains more details about the request made
            article_id: id of the article to be liked

        Return: Response showing that the article was liked
        """

        like = request.data.get('article', {})

        user_data = JWTAuthentication().authenticate(request)

        like["author"] = user_data[1]

        like["article_id"] = article_id

        serializer = self.serializer_class(data=like)
        serializer.is_valid(raise_exception=True)
        result = serializer.perform_save(like)
        return Response(result)

    def delete(self, request, article_id):
        """ This function is handling requests for deleting a like

        Args:
            request: contains more details about the request made
            article_id: id of the article to be deleted

        Return: Response showing that the article was deleted
        """
        serializer_data = request.data.get('article', {})

        user_data = JWTAuthentication().authenticate(request)

        serializer_data["author"] = user_data[1]
        serializer_data["article_id"] = article_id

        serializer = self.serializer_class(
            data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)

        result = serializer.perform_delete(serializer_data)

        return Response(result, status=status.HTTP_200_OK)


class ArticlesSearchFeed(ListAPIView):

    serializer_class = CreateArticleAPIViewSerializer
    renderer_classes = (ListArticlesJSONRenderer,)

    def get_queryset(self):
        queryset = Article.objects.all()

        title = self.request.query_params.get('title', None)
        if title is not None:
            title = re.sub(' +', ' ', title)
            queryset = queryset.filter(title__icontains=title)

        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author__username__icontains=author)

        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            new_q = []
            for article in queryset:
                for a_tag in article.tags.all():
                    if str(a_tag) == tag:
                        new_q.append(article)
            queryset = new_q

        if len(queryset) <= 0:
            raise NoResultsMatch

        return queryset
