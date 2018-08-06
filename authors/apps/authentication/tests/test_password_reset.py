from django.test import Client, TestCase
import json
import jwt
import os
from datetime import datetime, timedelta

from ..models import User
from django.conf import settings


class TestPasswordReset(TestCase):
    def setUp(self):
        self.email = "testuseremail@email.com"
        self.username = 'testing12'
        self.password = 'testuserpass'

        self.user_that_lost_password = {
            'user': {
                'email': self.email,
                "callbackurl": "https://www.youtube.com/"
            }
        }

        self.new_password_data = {
            'user': {
                'new_password': "new_Password@2018"
            }
        }

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.test_client = Client()

    def test_password_reset_endpoint(self):
        """
        Test to test that the password reset endpoint is hit successfully
        """
        response = self.test_client.post(
            "/api/user/reset_password/", data=json.dumps(self.user_that_lost_password),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_password_update_endpoint(self):
        """
        Test to test that the update password endpoint is hit successfully
        """
        response = self.test_client.post(
            "/api/user/new_password/{}/".format(self.token), data=json.dumps(self.new_password_data),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_password_update_endpoint_with_invalid_token(self):
        """
        """
        response = self.test_client.post(
            "/api/user/new_password/{}/".format("self.token123"), data=json.dumps(self.new_password_data),
            content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 400)

    def generate_token(self):
        dt = datetime.now() + timedelta(minutes=30)

        token = jwt.encode({
            'username': self.username,
            'email': self.email,
            'exp': int(dt.strftime('%s')),
            'call_back_url': os.getenv('CALL_BACK_URL')
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token`
        """
        return self.generate_token()
