from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.template.defaultfilters import slugify
import uuid
from ..authentication.backends import JWTAuthentication
from ..authentication.models import User

from .renderers import ArticlesJSONRenderer

from .serializers import (
    CreateArticleAPIViewSerializer
)


class CreateArticleAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticlesJSONRenderer,)
    serializer_class = CreateArticleAPIViewSerializer

    def post(self, request):
        article = request.data.get('article', {})

        # decode user token and return its value
        user_data = JWTAuthentication().authenticate(request)

        article["user_id"] = user_data[1]

        # create a an article slug fron title
        slug = slugify(article["title"]).replace("_", "-")
        slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
        article["slug"] = slug

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Article created successfully."}, status=status.HTTP_201_CREATED)
