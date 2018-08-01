from django.contrib.auth import authenticate
from django.core.validators import URLValidator
# from django.core.validators import ValidationError
from rest_framework import serializers

from .models import User

import re

from ..email.email import Mailer

# from .social_auth.google import google_auth
from .social_auth import google, facebook_auth


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # characters, and can not be read by the client.
    password = serializers.CharField(
        write_only=True
    )
    callbackurl = serializers.URLField(write_only=True)

    # make sure email os of email length
    email = serializers.EmailField()
    username = serializers.CharField()
    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        # return a success message on succeesful registration
        fields = ['email', 'username', 'password', 'callbackurl']

    # https://stackoverflow.com/questions/29813463/django-rest-framework-email-validation
    def validate_email(self, email_var):
        # Check if email address is already in use by another user
        db_email = User.objects.filter(email=email_var)
        if db_email.exists():
            raise serializers.ValidationError(
                "The email address you have used is already registered.")
        elif Mailer.verify_email_exists(email_var) is False:
            raise serializers.ValidationError(
                "Please check if your email is valid")
        else:
            return email_var

    # https://stackoverflow.com/questions/29813463/django-rest-framework-email-validation
    def validate_username(self, username_var):
        # check if user name already exists in the database
        # check if username is between 6 to 255 chracters
        # make sure username can only contain underscore characters included with alphanumeric characters
        db_username = User.objects.filter(username=username_var)
        if len(username_var) >= 25 or len(username_var) < 5:
            raise serializers.ValidationError(
                "The username can only be between 5 to 25 characters.")
        elif not re.match("^[A-Za-z0-9_]*$", username_var):
            raise serializers.ValidationError(
                "Username only takes letters, numbers, and underscores.")
        elif db_username.exists():
            raise serializers.ValidationError(
                "The username you have used is already taken.")
        else:
            return username_var

    # https://stackoverflow.com/questions/29813463/django-rest-framework-email-validation
    def validate_password(self, password_var):
        # Check if password is is between 8 to 128 characters
        # check if password contains upper case letters, numbers and special characters
        if len(password_var) < 8:
            raise serializers.ValidationError(
                "Password cannot be less than 8 characters.")
        elif len(password_var) >= 128:
            raise serializers.ValidationError(
                "Password cannot be more than 128 characters.")
        elif password_var.isalnum() or re.search('[0-9]|[A-Z]', password_var) is None:
            raise serializers.ValidationError(
                "Password must at least contain a capital letter or number and special character.")
        else:
            return password_var

    # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    def validate_callbackurl(self, url_var):
        # verify that the url that was passed is a valid url.

        if not URLValidator(url_var):
            raise serializers.ValidationError('the url is not a valid')
        else:
            return url_var

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        # But take remove the callbackurl as its not required by the
        # create_user function.
        validated_data.pop('callbackurl')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'The email or password is incorrect.'
            )

        # A user needs to have their account verified for a successful registration
        if not user.is_verified:
            raise serializers.ValidationError(
                'Please check your email and verify account'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token',)

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class GoogleSocialAuthAPIViewSerializer(serializers.Serializer):
    """ Handles all social auth related tasks from google """

    # get google authentication token from and do validations
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        # create an instance of the google social auth lib and validate token
        user_info = google.google_auth.validate(auth_token)

        # check if google managed to decode token
        # this is by checking if key sub exists
        try:
            user_info['sub']
        except:  # noqa: E722
            msg = 'The token is either invalid or expired. Please login again.'
            raise serializers.ValidationError(
                msg
            )

        # check if the user id fron decoded token exists in the decoded token dict
        user = User.objects.filter(social_id=user_info['sub'])

        # if user does not exist, register the user into the database.
        # i.e. create a new user
        if not user.exists():
            user = {
                'username': user_info['name'], 'email': user_info['email'], 'password': 'jndhbcdhbch'}
            try:
                User.objects.create_user(**user)
            except:  # noqa: E722
                msg = 'User with email ' + \
                    user_info['email'] + ' aleady exists.'
                raise serializers.ValidationError(
                    msg
                )
            User.objects.filter(email=user_info['email']).update(
                social_id=user_info['sub'])
            auth = authenticate(
                email=user_info['email'], password="jndhbcdhbch")
            return {
                auth.token
            }
        else:
            # if user already exists and is authenticated by google also,
            # return the user an authentication token
            auth = authenticate(
                email=user_info['email'], password="jndhbcdhbch")
            return auth.token


class FacebookSocialAuthAPIViewSerializer(serializers.Serializer):
    """ Handles all social auth related tasks from google """

    # get google authentication token from and do validations
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        # create an instance of the google social auth lib and validate token
        user_info = facebook_auth.FacebookValidate.validate(auth_token)

        # check if google managed to decode token
        # this is by checking if key sub exists
        try:
            user_info['id']
        except:  # noqa: E722
            msg = 'The token is either invalid or expired. Please login again.'
            raise serializers.ValidationError(
                msg
            )

        # check if the user id fron decoded token exists in the decoded token dict
        user = User.objects.filter(social_id=user_info['id'])

        # if user does not exist, register the user into the database.
        # i.e. create a new user
        if not user.exists():
            user = {
                'username': user_info['name'], 'email': user_info['email'], 'password': 'jndhbcdhbch'}

            # create a new facebook user
            try:
                User.objects.create_user(**user)
            except:  # noqa: E722
                msg = 'User with email ' + \
                    user_info['email'] + ' aleady exists.'
                raise serializers.ValidationError(
                    msg
                )
            User.objects.filter(email=user_info['email']).update(
                social_id=user_info['id'])
            auth = authenticate(
                email=user_info['email'], password="jndhbcdhbch")
            return {
                auth.token
            }
        else:
            # if user already exists and is authenticated by google also,
            # return the user an authentication token
            auth = authenticate(
                email=user_info['email'], password="jndhbcdhbch")
            return auth.token


class VerificationSerializer(serializers.Serializer):
    """Serialises verification requests and verifys the user."""

    def verify_user(self, data):
        # check if the token data has a username key, and raise an error
        # if it doesnot exist.
        if 'username' not in data:
            raise serializers.ValidationError(
                {'token': 'The token is either invalid. Please login to continue.'}
            )
        # The `verify_user` method is where the update actually occurs.Here, we
        # check if the user exists in the system.If the user does exist we go
        # ahead and verify that user's account and raise an error if they
        # do not exist or if the account has already been verified.
        user = User.objects.filter(
            username=data['username']).values('is_verified')
        if not user.exists():
            raise serializers.ValidationError(
                {'username': 'This user does not exist.'}
            )
        elif user[0]['is_verified'] is True:
            raise serializers.ValidationError(
                {'username': 'The account is already verified.'}
            )
        else:
            user.update(is_verified=True)

        return {
            'user': 'Your account is verified, continue to login'
        }
