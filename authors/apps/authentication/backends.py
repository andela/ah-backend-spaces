import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

"""Configure JWT Here"""


class JWTAuthentication:

    def __init__(self):
        """
        Create a class instance here
        """
        pass

    def authenticate(self, user_token):
        """
        Check Authenticity of a user token here
        """
        pass
