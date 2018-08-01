from django.test import Client
from django.test import TestCase
import json
import os
from ..models import User
from ...email.email import TokenGenerator


class BaseTest(TestCase):

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()
        self.token_class = TokenGenerator()
        # users used to register
        self.user_to_register = {
            'user': {
                'username': 'Aurthurs',
                'email': 'haven.authors@gmail.com',
                'password': 'jakejake@20AA',
                'callbackurl': 'https://example.com'
            }
        }
        self.user_to_register_with_no_credentials = {
            "user": {
                "username": "",
                "email": "",
                "password": "",
                'callbackurl': 'https://example.com'
            }
        }
        self.user_to_register_with_invalid_email = {
            "user": {
                "username": "johns",
                "email": "",
                "password": "complex_password",
                'callbackurl': 'https://example.com'
            }
        }

        # users used to login
        self.email = 'boomboom@gmail.com'
        self.username = 'boomboom'
        self.password = 'boompass'

        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        self.user.is_verified = True
        self.user.save()

        self.registred_user_to_login = {
            "user": {
                "email": self.email,
                "password": self.password
            }
        }
        self.un_registred_user_to_login = {
            "user": {
                "email": "jake@jake21.jake",
                "password": "jakejake21"
            }
        }
        self.un_named_user_to_login = {
            "user": {
                "email": "",
                "password": "jakejake21"
            }
        }
        self.anonymous_user_to_login = {
            "user": {
                "username": "",
                "password": ""
            }
        }
        self.wrong_credentials_user_to_login = {
            "user": {
                "email": "jake@jake21.jake",
                "password": "jakejake"
            }
        }
        self.hacking_user_can_crash_login = {
            "user": {
                "": "jake@jake.jake",
                "password": "jakejake"
            }
        }
        self.invalid_string_user_to_login = {
            "user": {
                "email": "jake@jake.jake",
                "password": ["jakejake"
                             ]
            }
        }
        self.user_with_weak_password = {
            "user": {
                "password": "weak password"
            }
        }
        self.password_less_than_eight = {
            "user": {
                "email": "jake@jake21.jake",
                "password": "w#4Ag^ "
            }
        }
        self.username_less_than_six = {
            "user": {
                "email": "jake@jake21.jake",
                "username": "josh",
            }
        }
        self.user_with_long_username = {
            "user": {
                "email": "jake@jake21.jake",
                "username": "g_" * 13,
            }
        }
        self.password_greater_than_128 = {
            "user": {
                "email": "jake@jake21.jake",
                "password": "j$55AAA^&&" * 30
            }
        }
        self.user_with_non_alpha_username = {
            "user": {
                "email": "jake@jake21.jake",
                "username": "joshua@3334^$"
            }
        }

        self.user_with_invalid_social_token = {
            "user": {
                "auth_token": "fake_fb_twitter_or_google_token"
            }
        }

        self.facebook_debug_token = {
            "user": {
                "auth_token": os.getenv('FACEBOOK_DEBUG_TOKEN')
            }
        }

        self.google_debug_token = {
            "user": {
                "auth_token": os.getenv('GOOGLE_DEBUG_TOKEN')
            }
        }

        self.user_registered = self.register_user(self.user_to_register)
        self.user_logged_in = self.login_user(self.registred_user_to_login)

        # Make a token to send to the registered user, token to be used
        # in verifying the registred user
        registered_user_data = {
            'username': self.username,
            'email': self.email,
            'callbackurl': 'https://example.com'
        }

        self.encorded_token = self.token_class.make_custom_token(
            registered_user_data)

        # Use to check if an unregistred username can verify account.Here we
        # change just the username to the new name we want to use.
        registered_user_data['username'] = "un_registred_username"
        self.encorded_invalid_uname = self.token_class.make_custom_token(
            registered_user_data)

    def register_user(self, user_details_dict):
        """ Register anew user to the system

        Args:
            user_details_dict: a dictionary with username, email, password of the user

        Returns: an issued post request to the user registration endpoint
        """
        return self.test_client.post(
            "/api/users/", data=json.dumps(user_details_dict), content_type='application/json')

    def login_user(self, user_details_dict):
        """Authenticate the user credentials and login

        Args:
            user_details_dict: a dictionary with email and password of the user.

        Returns: an issued post request to the user Authentication endpoint.
        """
        return self.test_client.post(
            "/api/users/login/", data=json.dumps(user_details_dict), content_type='application/json')

    def fetch_current_user(self, user_token):
        """ Fetch the current logged in user.

        Args:
            user_token: a unique generated encrypted code that has user details.

        Returns: an issued get request to the get current user endpoint.
        """

        return self.test_client.get("/api/user/", headers="user_token")

    def verify_user_account(self, user_token):
        """ Verify a user who wants to get their account verified.

        Args:
            user_token: a unique generated encrypted code that has user details.

        Returns: an issued get request to the verify user endpoint.
        """
        return self.test_client.get("/api/activate/{}".format(user_token))

    def tearDown(self):
        pass


class TestRegistration(BaseTest):
    """ TestRegistration has tests that validate a user before registeration """

    def test_user_can_signup(self):
        """ test a user can sign up for an account """

        response = self.user_registered
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()[
                         'user']['message'], 'You were succesfull registered! Please check ' +
                         self.user_to_register["user"]["email"] + ' for a verification link.')

    def test_user_can_duplicate_registration(self):
        """ test if auser can create an acount twice """

        response = response = self.user_registered
        self.assertEqual(response.status_code, 201)

        response2 = self.register_user(self.user_to_register)
        self.assertEqual(response2.status_code, 400)

    def test_user_can_register_with_no_credentials(self):
        """ test a user can register with no email, username or password """

        response = self.register_user(
            self.user_to_register_with_no_credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['email'], [
                         u'This field may not be blank.'])
        self.assertEqual(response.json()['errors']['username'], [
                         u'This field may not be blank.'])
        self.assertEqual(response.json()['errors']['password'], [
                         u'This field may not be blank.'])

    def test_user_can_register_with_invalid_email(self):
        " test if a user can create an account with a bad email"

        response = self.register_user(self.user_to_register_with_invalid_email)

        print(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['email'], [
                         u'This field may not be blank.'])

    def test_user_signup_weak_password(self):
        """ test if a user can signup with a weak password """
        response = self.register_user(
            self.user_with_weak_password)
        self.assertEqual(response.json()['errors']['password'], [
                         "Password must at least contain a capital letter or number and special character."])

    def test_signup_with_password_less_eight(self):
        """ test if a user can signup with a password less than 8 """
        response = self.register_user(
            self.password_less_than_eight)
        self.assertEqual(response.json()['errors']['password'], [
                         'Password cannot be less than 8 characters.'])

    def test_signup_with_long_password(self):
        """ test if a user can signup with a username longer than 128 """
        response = self.register_user(
            self.password_greater_than_128)
        self.assertEqual(response.json()['errors']['password'], [
                         'Password cannot be more than 128 characters.'])

    def test_signup_with_short_username(self):
        """ test if a user can signup with a username less than six characters """
        response = self.register_user(
            self.username_less_than_six)
        self.assertEqual(response.json()['errors']['username'], [
                         'The username can only be between 5 to 25 characters.'])

    def test_signup_with_non_alpha_username(self):
        """ test if a user can signup with a username that is non alphanumeric """
        response = self.register_user(
            self.user_with_non_alpha_username)
        self.assertEqual(response.json()['errors']['username'], [
                         'Username only takes letters, numbers, and underscores.'])

    def test_username_greater_than_25(self):
        """ test if a user can signup with a username greater than 25 """
        response = self.register_user(
            self.user_with_long_username)
        self.assertEqual(response.json()['errors']['username'], [
                         'The username can only be between 5 to 25 characters.'])

    def test_signup_with_invalid_fb_token(self):
        """ test if a user can signup with wrong facebook token """

        response = self.test_client.post(
            "/api/auth/facebook/", data=json.dumps(
                self.user_with_invalid_social_token), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['auth_token'], [
                         'The token is either invalid or expired. Please login again.'])

    def test_signup_with_invalid_google_token(self):
        """ test if a user can signup with wrong google token """

        response = self.test_client.post(
            "/api/auth/google/", data=json.dumps(
                self.user_with_invalid_social_token), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['auth_token'], [
                         'The token is either invalid or expired. Please login again.'])


class TestAccountVerification(BaseTest):
    """ TestAccountVerification has tests to ensure that an authentic user can verify their account"""

    def test_user_can_verify_account(self):
        """test if a user can verify their account"""

        # Create a new user
        self.register_user(self.user_to_register)

        # Grab only the relevant items and generate the token
        user_to_register = self.user_to_register['user']
        user_to_register.pop('password')
        encoded_token = self.token_class.make_custom_token(user_to_register)

        # Verify user
        user_verify_account = self.verify_user_account(encoded_token)
        self.assertEqual(user_verify_account.status_code, 302)

        # Login the same user
        self.user_to_register['user']['password'] = 'jakejake@20AA'
        verifired_user_login = self.login_user(self.user_to_register)
        self.assertEqual(verifired_user_login.status_code, 200)

    def test_user_can_verify_already_account_verified(self):
        """test a user can verify a verified account"""
        verified_account = self.verify_user_account(
            self.encorded_token)
        self.assertEqual(verified_account.status_code, 400)
        self.assertEqual(verified_account.json()[
                         'errors']['username'], 'The account is already verified.')

    def test_user_verify_with_fake_token(self):
        """test if a user can verify account with a fake token"""
        user_verify_account = self.verify_user_account(
            self.encorded_token + "ehwfv")
        self.assertEqual(user_verify_account.status_code, 400)
        self.assertEqual(user_verify_account.json()[
                         'token'], "token is invalid")

    def test_un_registered_username_verify_account(self):
        """test if un registered username can verify their account"""
        user_verify_account = self.verify_user_account(
            self.encorded_invalid_uname)
        self.assertEqual(user_verify_account.status_code, 400)
        self.assertEqual(user_verify_account.json()['errors'][
                         'username'], "This user does not exist.")

    def test_un_named_username_verify_account(self):
        """test if an un-named username can verify their account"""

        # Use to check if a token with out a username can verify account.Here we
        # change just the remove the usename key from the dictionary.
        registered_user_data = {
            'username': self.username,
            'email': self.email,
            'callbackurl': 'https://example.com'
        }
        registered_user_data.pop('username')
        no_username_invalid_uname = self.token_class.make_custom_token(
            registered_user_data)

        user_verify_account = self.verify_user_account(
            no_username_invalid_uname)
        self.assertEqual(user_verify_account.status_code, 400)
        self.assertEqual(user_verify_account.json()['errors'][
                         'token'], "The token is either invalid. Please login to continue.")


class TestAuthentication(BaseTest):
    """ TestAuthentication has tests to ensure that an authentic user can login to the system """

    def test_user_can_login(self):
        """ test checks if a registed user login to the system """

        response = self.user_registered
        self.assertEqual(response.status_code, 201)

        login_response = self.user_logged_in
        self.assertEqual(login_response.status_code, 200)

    def test_unregistered_user_can_login(self):
        """ test if a user who has not created an account can register """

        login_response = self.login_user(self.un_registred_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['error'], [
                         'The email or password is incorrect.'])

    def test_login_without_username(self):
        """ test if a user can login without a username """

        login_response = self.login_user(self.un_named_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['email'], [
                         'This field may not be blank.'])

    def test_login_without_credentials(self):
        """ test if a user can login without using username and password """

        login_response = self.login_user(self.anonymous_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['email'], [
                         'This field is required.'])
        self.assertEqual(login_response.json()['errors']['password'], [
                         'This field may not be blank.'])

    def test_wrong_credentials_user_login(self):
        """ test if a user with wrong credentials can login """

        login_response = self.login_user(self.wrong_credentials_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['error'], [
                         'The email or password is incorrect.'])

    def test_invalid_string_user_login(self):
        """ test if a user with invalid characters in their strings can login """

        response = self.login_user(self.invalid_string_user_to_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['password'], [
                         u'Not a valid string.'])

    def test_hacking_user_can_crash_login(self):
        """ test if a user with invalid characters in their strings can login """
        response = self.login_user(self.hacking_user_can_crash_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['email'], [
                         u'This field is required.'])

    def test_facebook_login(self):
        """ test if social login is possible with facebook token """
        response = self.test_client.post(
            "/api/auth/facebook/", data=json.dumps(self.facebook_debug_token), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_facebook_signin_after_registration(self):
        """ test if facebook login is possible when user is already registered """
        response1 = self.test_client.post(
            "/api/auth/facebook/", data=json.dumps(self.facebook_debug_token), content_type='application/json')
        self.assertEqual(response1.status_code, 200)

        response2 = self.test_client.post(
            "/api/auth/facebook/", data=json.dumps(self.facebook_debug_token), content_type='application/json')
        self.assertEqual(response2.status_code, 200)


class TestRouteMethods(BaseTest):
    """ TestRouteMethods: tests the request methods of the endpoint """

    def test_can_login_with_put(self):
        """ test if a user can login using a put"""
        response = self.test_client.put(
            "/api/users/login/", data=json.dumps(self.registred_user_to_login), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['user']
                         ['detail'], u'Method "PUT" not allowed.')


class TestUserRetrivalAndUpdate(BaseTest):
    """
    class to user retrival and update endpoints
    """

    def test_update_user(self):
        """
        Test to check the user update endpoint
        """

        self.johndoe = {
            'user': {
                'username': "johndoe",
                'email': "johndoe@mail.com",
                'password': "johndoespass",
            }
        }

        johndoe_user = User.objects.create_user(
            'johndoe', 'johndoe@mail.com', 'johndoespass')
        johndoe_user.is_verified = True
        johndoe_user.save()

        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(self.johndoe), content_type='application/json')
        token = response.json()['user']['token']

        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        self.nolonger_johndoe = {
            'user': {
                'username': 'peterparker',
                'email': 'peterparker@gmail.com'
            }
        }

        response = self.test_client.put(
            "/api/user/", **headers, data=json.dumps(self.johndoe), content_type='application/json')

        self.assertEqual(response.status_code, 200)
