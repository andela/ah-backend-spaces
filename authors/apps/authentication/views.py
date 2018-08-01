from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from ..email.email import Mailer, TokenGenerator, datetime, timedelta, os


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

        expiration_time = datetime.now() + timedelta(days=60)
        user_data = {
            'username': serializer.data['username'],
            'email': serializer.data['email'],
            'exp': int(expiration_time.strftime('%s')),
            'call_back_url': os.getenv('CALL_BACK_URL')
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
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
