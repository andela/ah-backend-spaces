from django.test import TestCase, Client

import json

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile


class TestProfileViews(TestCase):
    def setUp(self):
        """ Funtion to setup some code that will be needed for unittests """
        self.email = 'boomboom@gmail.com'
        self.username = 'testing12'
        self.password = 'testuserpass'

        # test user to be followed
        self.followee_username = 'popularguy'
        self.followee_email = 'popular.guy@gmail.com'
        User.objects.create_user(
            self.followee_username, self.followee_email, self.password)

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        # profile of the follower
        self.follower_profile = self.user.profile

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

    def login_a_user(self):
        """
        Reusable function to login a user
        """

        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(self.data), content_type='application/json')
        token = response.json()['user']['token']
        return token

    @property
    def token(self):
        return self.login_a_user()

    def follow_a_user(self):
        self.follower_profile.follow(Profile.objects.get(
            user__username=self.followee_username))
        self.follower_profile.save()

    def test_retrieve_profile(self):
        """ test for the retrive profile endpoint """
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_retrieve_profile_that_doesnt_exist(self):
        """ test for attempt to retrieve a profile that doesn't exit"""
        response = self.test_client.get(
            "/api/profiles/{}/".format("someusername"), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_follow_a_user(self):
        """ test for following a user endpoint """
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.post(
            "/api/profiles/{}/follow/".format(self.followee_username), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 201)

    def test_un_follow_a_user(self):
        """ test for unfollowing a user endpoint"""
        self.follow_a_user()
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.delete(
            "/api/profiles/{}/follow/".format(self.followee_username), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)

    def test_follow_a_non_existant_profile(self):
        """ test for attempt to follow a user that is not in the db"""
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.post(
            "/api/profiles/{}/follow/".format("non_existant_person"), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)

    def test_un_follow_a_non_existant_profile(self):
        """ test for attempt to unfollow a user that is not in the db"""
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.delete(
            "/api/profiles/{}/follow/".format("non_existant_person"), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)

    def test_user_attempt_following_themselves(self):
        """ test for attempt by user to follow themselves """
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.post(
            "/api/profiles/{}/follow/".format(self.username), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)

    def test_user_attempt_to_follow_user_they_following(self):
        self.follow_a_user()
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.post(
            "/api/profiles/{}/follow/".format(self.followee_username), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)

    def test_user_attempt_to_un_follow_user_they_are_not_following(self):
        self.follow_a_user()
        self.follower_profile.unfollow(Profile.objects.get(
            user__username=self.followee_username))
        self.follower_profile.save()
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }
        response = self.test_client.delete(
            "/api/profiles/{}/follow/".format(self.followee_username), **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)
