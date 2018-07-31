import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

"""Configure JWT Here"""


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        method called on every request regardless of
        whether the endpoint requires authentication.
        """
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The Token string should not contain spaces.
            return None

        # decode prefix and token values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Method to try and authenticate the given credentials.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:  # noqa: E722
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)

    def authenticate_header(self, request):
        return 'Token'
