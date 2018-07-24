from django.test import TestCase
from ..models import User, UserManager


class TestUser(TestCase):
    """ Test module for User """

    def setUp(self):
        User.objects.create(username="testuser", email = "testuser@email.com", is_active = True, is_staff=True)

    def test_get_full_name(self):
        """ test get_full_name property"""
        user1 = User.objects.get(email="testuser@email.com")
        self.assertEqual(user1.get_full_name, "testuser")

    def get_short_name(self):
        """ test get_shortname property"""
        user1 = User.objects.get(email="testuser@email.com")
        self.assertEqual(user1.get_short_name, "testuser")

    def test_create_user(self):
        """ test module for successfully creating user"""
        created_user = User.objects.create_user(username = 'testhghguser', email='tesuyuyytuser@email.com')
        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        self.assertEqual(created_user, user1)

    def test_create_super_user(self):
        """ test module for successfully creating super user """
        created_user = User.objects.create_superuser(username = 'testhghguser', email='tesuyuyytuser@email.com', password='secret')
        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        self.assertEqual(created_user, user1)






