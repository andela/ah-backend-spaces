from django.test import TestCase
from ..models import User, UserManager


class TestUser(TestCase):
    """ """

    def setUp(self):
        """ test if objects is an instance of UserManager"""
        self.objects = UserManager()
        self.assertIsInstance(self.objects, UserManager)

    def test_create_user_without_username(self):
        """ test if function 'create_user()' can create a user without a username """
        with self.assertRaises(TypeError) as type_error:
            User.objects.create_user(
                username=None, email="tesuyuyytuser@email.com")
        self.assertTrue(
            "Users must have a username." in str(type_error.exception))

    def test_create_user_without_email(self):
        """ test if function 'create_user()' can create a user without a username """
        with self.assertRaises(TypeError) as type_error:
            User.objects.create_user(
                username="ssewilliam", email=None)
        self.assertTrue(
            "Users must have an email address." in str(type_error.exception))

    def test_create_superuser_without_password(self):
        """ test if function 'create_superuser()' can create a super user without the password argument"""
        with self.assertRaises(TypeError) as type_error:
            User.objects.create_superuser(
                username='testuser', email='tesuyuyytuser@email.com', password=None)
        self.assertTrue(
            "Superusers must have a password." in str(type_error.exception)
        )
