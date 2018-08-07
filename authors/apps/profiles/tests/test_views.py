from django.test import TestCase, Client

import json

from authors.apps.authentication.models import User


class TestProfileViews(TestCase):
    def setUp(self):
        """ Funtion to setup some code that will be needed for unittests """
        self.email = 'boomboom@gmail.com'
        self.username = 'testing12'
        self.password = 'testuserpass'

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        # verify a user's account and save
        self.user.is_verified = True
        self.user.save()

        self.data = {
            'user': {
                'username': self.username,
                'email': self.email,
                'password': self.password,
            }
        }

        self.test_client = Client()

    def tearDown(self):
        pass

    def test_retrieve_profile(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_retrieve_profile_that_doesnt_exist(self):
        response = self.test_client.get(
            "/api/profiles/{}/".format("someusername"), content_type='application/json')
        self.assertEqual(response.status_code, 400)
