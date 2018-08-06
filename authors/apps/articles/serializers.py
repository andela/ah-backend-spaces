from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import Article


class CreateArticleAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['title', 'body', 'description',
                  'user_id', 'slug', 'published', 'created_at']
