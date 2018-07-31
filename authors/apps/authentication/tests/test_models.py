from django.test import TestCase
from ..models import User, UserManager
import jwt
from django.conf import settings
from datetime import datetime, timedelta


class TestUser(TestCase):
    """ Test module for User """

    def setUp(self):
        """ Setup some code that is used by the unittests"""
        User.objects.create(
            username="testuser", email="testuser@email.com", is_active=True, is_staff=True)
        User.objects.create(
            username="testuser2", email="testuser2@email.com", is_active=True, is_staff=False)

        # test if objects is an instance of UserManager
        self.objects = UserManager()
        self.assertIsInstance(self.objects, UserManager)

    def test_string_representation(self):
        """ test for the value returned by __str__ """
        user1 = User.objects.get(email="testuser@email.com")
        self.assertEqual(str(user1), "testuser@email.com")

    def test_get_full_name(self):
        """ test get_full_name property"""
        user1 = User.objects.get(email="testuser@email.com")
        user2 = User.objects.get(email="testuser2@email.com")

        self.assertEqual(user1.get_full_name, "testuser")
        self.assertEqual(user2.get_full_name, "testuser2")

    def test_get_short_name(self):
        """ test get_shortname property"""
        user1 = User.objects.get(email="testuser@email.com")
        user2 = User.objects.get(email="testuser2@email.com")
        self.assertEqual(user1.get_short_name(), "testuser")
        self.assertEqual(user2.get_short_name(), "testuser2")

    def test_create_user(self):
        """ test module for successfully creating user"""
        created_user = User.objects.create_user(
            username='testhghguser', email='tesuyuyytuser@email.com')
        created_user2 = User.objects.create_user(
            username='gideon', email='gideon@email.com', password='gideon123')

        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        user2 = User.objects.get(email="gideon@email.com")

        self.assertEqual(created_user, user1)
        self.assertEqual(created_user2, user2)
        self.assertEqual(user1.is_staff, False)
        self.assertEqual(created_user.get_full_name, "testhghguser")

    def test_create_super_user(self):
        """ test module for successfully creating super user """
        created_user = User.objects.create_superuser(
            username='testhghguser', email='tesuyuyytuser@email.com', password='secret')
        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        self.assertEqual(created_user, user1)

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

    def test_username_can_exceed_255(self):
        username = "x" * 256
        user1 = User.objects.create(
            username=username, email="testusernames@email.com", is_active=True, is_staff=False)
        user1 = User.objects.get(email="testusernames@email.com")
        self.assertEqual(user1.get_short_name(), username)
