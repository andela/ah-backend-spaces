from django.test import Client
from django.test import TestCase
from authors.apps.authentication.models import User
import json


class BaseTest(TestCase):

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()

        self.article_to_create = {
            "article": {
                "title": "hahahhaha hahaha hahah ahhah",
                "body": "<p>this is a body that is here hahahhahaha\n </p>",
                "description": "this is another article hahahhaha"
            }
        }

        self.user_to_login = {
            'user': {
                'email': 'haven.authors@gmail.com',
                'password': 'jakejake@20AA'
            }
        }

        # Create a verified user
        johndoe_user = User.objects.create_user(
            'Aurthurs', 'haven.authors@gmail.com', 'jakejake@20AA')
        johndoe_user.is_verified = True
        johndoe_user.save()

        self.user_logged_in = self.login_user(self.user_to_login)

    def login_user(self, user_details_dict):
        """Authenticate the user credentials and login

        Args:
            user_details_dict: a dictionary with email and password of the user.

        Returns: an issued post request to the user Authentication endpoint.
        """
        return self.test_client.post(
            "/api/users/login/", data=json.dumps(user_details_dict),
            content_type='application/json')

    def tearDown(self):
        pass


class TestArticles(BaseTest):

    def test_create_article(self):

        # log the user in to get auth token
        response = self.user_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to create an article
        response = self.test_client.post(
            "/api/articles/", **headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['article']['message'], 'Article created successfully.')
