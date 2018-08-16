from django.test import Client
from django.test import TestCase

from authors.apps.authentication.models import User
import json


class BaseTest(TestCase):
    """ BaseTest: this class will be used by other tests classes and is
    responsible for operations with other classes.
    """

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()

        # Create a verified user
        johndoe_user = User.objects.create_user(
            'Aurthurs', 'haven.authors@gmail.com', 'jakejake@20AA')
        johndoe_user.is_verified = True
        johndoe_user.save()

        self.user_to_login = {
            "user": {
                'username': 'Aurthurs',
                'email': 'haven.authors@gmail.com',
                'password': 'jakejake@20AA'
            }
        }
        # content to post to article to like
        self.article_to_like = {
            "article": {
                "article_like": True
            }
        }

        self.null_article_to_like = {
            "article": {
                "article_like": None
            }
        }

        self.article_to_dis_like = {
            "article": {
                "article_like": False
            }
        }
        # content to post to article to favourite
        self.article_to_favourite = {
            "article": {
                "article_favourite": True
            }
        }
        self.article_to_favourite_with_false = {
            "article": {
                "article_favourite": False
            }
        }
        self.null_article_to_favourite = {
            "article": {
                "article_favourite": None
            }
        }

        self.article_to_un_favourite = {
            "article": {
                "article_favourite": False
            }
        }
        self.article_to_un_favourite_with_true = {
            "article": {
                "article_favourite": True
            }
        }
        # article to create
        self.article_to_create = {
            "article": {
                "title": "hahahhaha hahaha hahah ahhah",
                "body": "<p>this is a body that is here hahahhahaha\n </p>",
                "description": "this is another article hahahhaha"
            }
        }
        self.article_to_update = {
            "article": {
                "title": "This is an update",
                "body": "<p>This is the updated body\n </p>",
                "description": "This article had to be updated",
                "published": True
            }
        }

        self.user_logged_in = self.login_user(self.user_to_login)

    def login_user(self, user_details_dict):
        """Authenticate the user credentials anlogin

        Args:
            user_details_dict: a dictionary with email and password of the user.

        Returns: an issued post request to the user Authentication endpoint.
        """
        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(user_details_dict),
            content_type='application/json')

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        return {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }
