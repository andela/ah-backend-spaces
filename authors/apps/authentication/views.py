from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    GoogleSocialAuthAPIViewSerializer, FacebookSocialAuthAPIViewSerializer,
    VerificationSerializer, ResetPasswordSerializer, UpdatePasswordSerializer
)
from ..email.email import Mailer, TokenGenerator, datetime, timedelta, os
from .models import User


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer
    send_user_email = Mailer()
    token_class = TokenGenerator()

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # These are the values about the user that we need to send an email
        subject = "Confirm your account"
        template_name = 'verify_email.html'

        # Prepare to generate a token to be used in verifying that the user
        # `call_back_url` is the url that should be redirected to after
        # verifying the user.
        callback = {'url': user['callbackurl']}
        user_data = {
            'username': serializer.data['username'],
            'email': serializer.data['email'],
            'callbackurl': callback['url'],
        }

        # username to render in the verify email template
        # token to be used in verifying the user
        context = {
            'username': serializer.data['username'],
            'token': self.token_class.make_custom_token(user_data)
        }

        # send the user an email on successful registration
        self.send_user_email.send(
            serializer.data, subject, template_name, context)

        message = {"message": "You were succesfull registered! Please check " +
                   serializer.data["email"] + " for a verification link."}
        return Response(message, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """ funtion to update user information """
        user_data = request.data.get('user', {})

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'email': user_data.get('email', request.user.email),

            'profile': {
                'bio': user_data.get('bio', request.user.profile.bio),
                'image': user_data.get('image', request.user.profile.image)
            }
        }

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer_data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GoogleSocialAuthAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = GoogleSocialAuthAPIViewSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # pass data to serializer
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer
    send_user_email = Mailer()
    token_class = TokenGenerator()

    def post(self, request):
        user = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        # These are the values about the user that we need to send an email
        subject = "Reset password"
        template_name = 'reset_password.html'

        expiration_time = datetime.now() + timedelta(minutes=30)

        callback = {'url': user['callbackurl']}
        user_data = {
            'username': serializer.data['username'],
            'email': serializer.data['email'],
            'exp': int(expiration_time.strftime('%s'))
        }

        context = {
            'username': serializer.data['username'],
            'callbackurl': callback['url'],
            'token': self.token_class.make_custom_token(user_data)
        }

        # send the user an email on successful registration
        self.send_user_email.send(
            serializer.data, subject, template_name, context)

        message = {"message": "A password reset link has been sent " +
                   user["email"] + ", please check your email"}
        return Response(message, status=status.HTTP_200_OK)


class UpdatePasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = UpdatePasswordSerializer
    token_class = TokenGenerator()

    def post(self, request, token):
        new_password_data = request.data.get('user', {})

        decoded_token = self.token_class.decode_token(token)

        if not isinstance(decoded_token, dict):
            return Response({'token': 'token is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=decoded_token)
        serializer.validate_password(new_password_data['new_password'])
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=decoded_token['username'])
        user.set_password(new_password_data['new_password'])
        user.save()
        message = {"message": "Password has been successfully reset"}
        return Response(message, status=status.HTTP_200_OK)


class FacebookSocialAuthAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookSocialAuthAPIViewSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        # serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerificationSerializer
    token_class = TokenGenerator()

    def get(self, request, token):
        decoded_token = self.token_class.decode_token(token)

        if not isinstance(decoded_token, dict):
            return Response({'token': 'token is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        # We call the `serializer.update()` so as to update the data
        # If serializer.data returns an empty dictionary then user
        # is successfully registred else return data from the serializer.
        # Basically, a user can only verify their account once.

        serializer = self.serializer_class(data=decoded_token)
        serializer.is_valid(raise_exception=True)
        serializer.verify_user(decoded_token)

        if bool(serializer.data) is False:
            return HttpResponseRedirect(decoded_token['callbackurl'])
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
