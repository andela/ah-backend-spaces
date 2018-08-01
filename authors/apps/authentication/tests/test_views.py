from django.test import Client
from django.test import TestCase
import json
from ..models import User


class BaseTest(TestCase):

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()
        # users used to register
        self.user_to_register = {
            'user': {
                'username': 'Aurthurs',
                'email': 'haven.authors@gmail.com',
                'password': 'jakejake@20AA'
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

        self.user_registered = self.register_user(self.user_to_register)
        self.user_logged_in = self.login_user(self.registred_user_to_login)

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
