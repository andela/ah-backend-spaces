from django.test import Client
from django.test import TestCase
from authors.apps.authentication.models import User
from ..models import Notifications
from ...articles.tests.tests_views import BaseTest
from ...profiles.tests.test_views import TestProfileViews
import json


class TestNotifications(BaseTest):
    def test_fetch_notification(self):
        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.get(
            "/api/notifications/", **headers)
        self.assertEqual(response.status_code, 200)

    def test_mark_notificatin_as_read(self):
        """
        test if a user can mark a list of non existent notifications as read
        """
        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.put(
            "/api/notifications/", **headers,
            data=json.dumps(self.mark_as_read), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message']['notifications'], [1])

    def test_read_notification_for_non_existent(self):
        """
        test if a user can mark a list of non existent notifications as read
        """
        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.put(
            "/api/notifications/", **headers,
            data=json.dumps(self.mark_as_read_no_exitsent), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors']['error'], [
                         'The [8, 9] Id(s) do to exist.'])
