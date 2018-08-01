from django.test import TestCase, Client
from ..models import User
import json
import jwt
import authors.settings
from django.conf import settings
from datetime import datetime, timedelta


class TestJWT(TestCase):

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

    def test_existance_of_jwt(self):
        """
        Test to check if a token is actually generated on successful user registration
        """

        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(self.data), content_type='application/json')

        decoded_token = jwt.decode(
            response.json()['user']['token'], authors.settings.base.SECRET_KEY, 'HS256')

        self.assertTrue("token" in response.json()['user'])
        self.assertEqual(decoded_token['username'], self.username)

    def test_to_check_for_valid_token(self):
        """
        Test to check if a token is passed is valid the endpoint authorises the user
        """
        headers = {'HTTP_AUTHORIZATION': 'Token ' + self.token}

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_to_check_for_in_valid_token(self):
        """
        Test to check if a token passed is invalid
        """

        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token + 'werfasgs'
        }

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()[
                         'user']['detail'], "Invalid authentication. Could not decode token.")

    def test_no_actual_token_is_passed_in_header(self):
        """
        Test to check if no actual token is passed is valid the endpoint authorises the user
        """

        headers = {
            'HTTP_AUTHORIZATION': 'Token '
        }

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 401)

    def test_more_than_token_passed_in_header(self):
        """
        Test to check if a token is passed is valid the endpoint authorises the user
        """

        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token + ' somethingelse'
        }

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 401)

    def test_wrong_prefix_passed_in_header(self):
        """
        Test to check when a wrong prefix is passed in the header
        """

        headers = {
            'HTTP_AUTHORIZATION': 'Bear ' + self.token
        }

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 401)

    def test_token_passed_but_user_doesnt_exist(self):
        """
        Test to when token is passed is passed but user doesnt actually exist
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': 10,
            'exp': int(dt.strftime('%s')),
            'username': self.username
        }, settings.SECRET_KEY, algorithm='HS256')

        token = token.decode('utf-8')
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token
        }

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 401)

    def test_token_passed_but_user_is_not_active(self):
        """
        Test to check when a token is passed but user not active
        """

        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + self.token
        }

        # Deactivating user
        self.user.is_active = False
        self.user.save()

        response = self.test_client.get(
            "/api/user/", **headers, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 401)
