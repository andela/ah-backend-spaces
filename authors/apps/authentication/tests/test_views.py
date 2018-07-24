from django.test import Client
from django.test import TestCase
import json


class BaseTest(TestCase):

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()
        # users used to register
        self.user_to_register = {
            'user': {
                'username': 'Jacobs',
                'email': 'jake@jake.jake',
                'password': 'jakejake'
            }
        }
        self.user_to_register_with_no_credentials = {
            "user": {
                "username": "",
                "email": "",
                "password": ""
            }
        }
        self.user_to_register_with_invalid_email = {
            "user": {
                "username": "johns",
                "email": "",
                "password": "complex_password"
            }
        }
        # users used to login
        self.registred_user_to_login = {
            "user": {
                "email": "jake@jake.jake",
                "password": "jakejake"
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

        self.user_registered = self.register_user(self.user_to_register)
        self.user_logged_in = self.login_user(self.registred_user_to_login)

    def register_user(self, user_details_dict):
        """ Register anew user to the system

        Args:
            user_details_dict: a dictionary with username, email, password of the user

        Returns: an issued post request to the user registration endpoint
        """
        return self.test_client.post(
            "/api/users", data=json.dumps(user_details_dict), content_type='application/json')

    def login_user(self, user_details_dict):
        """Authenticate the user credentials and login

        Args: 
            user_details_dict: a dictionary with email and password of the user.

        Returns: an issued post request to the user Authentication endpoint.
        """
        return self.test_client.post(
            "/api/users/login", data=json.dumps(user_details_dict), content_type='application/json')

    def fetch_current_user(self, user_token):
        """ Fetch the current logged in user.

        Args:
            user_token: a unique generated encrypted code that has user details.

        Returns: an issued get request to the get current user endpoint.
        """

        return self.test_client.get("/api/user", headers="user_token")

    def tearDown(self):
        pass


class TestRegistration(BaseTest):
    """ TestRegistration has tests that validate a user before registeration """

    def test_user_can_signup(self):
        """ test a user can sign up for an account """

        response = self.user_registered
        self.assertEqual(response.status_code, 201)

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
        # self.assertEqual(response.content['message'],"hello")
        self.assertEqual(response.json()['errors']['email'], [
                         u'This field may not be blank.'])


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
                         b'A user with this email and password was not found.'])

    def test_login_without_username(self):
        """ test if a user can login without a username """

        login_response = self.login_user(self.un_named_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['email'], [
                         b'This field may not be blank.'])

    def test_login_without_credentials(self):
        """ test if a user can login without using username and password """

        login_response = self.login_user(self.anonymous_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['email'], [
                         b'This field is required.'])
        self.assertEqual(login_response.json()['errors']['password'], [
                         b'This field may not be blank.'])

    def test_wrong_credentials_user_login(self):
        """ test if a user with wrong credentials can login """

        login_response = self.login_user(self.wrong_credentials_user_to_login)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json()['errors']['error'], [
                         b'A user with this email and password was not found.'])

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


class TestUserRetrieve(BaseTest):
    """ TestUserRetrieve: tests if a current user is returned """

    def test_current_user_is_retrieved(self):
        # response = self.fetch_current_user("asdf")
        # self.assertEqual(response.status_code,200)
        pass

class TestUserUpdate(BaseTest):
    """TestUserUpdate: tests if a current user can update their details """

    def test_current_user_update_details(self):
        """ test if the current logged in user can update details """
        # response = self.test_client.put("/api/user", headers="user_token", content_type="application/json")
        # self.assertEqual(response.status_code,200)
        pass

class TestRouteMethods(BaseTest):
    """ TestRouteMethods: tests the request methods of the endpoint """

    def test_can_login_with_put(self):
        """ test if a user can login using a put"""
        response = self.test_client.put(
            "/api/users/login", data=json.dumps(self.registred_user_to_login), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['user']
                         ['detail'], u'Method "PUT" not allowed.')
