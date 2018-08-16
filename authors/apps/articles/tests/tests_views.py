from django.test import Client
from django.test import TestCase
from ...articles.models import Article
from authors.apps.authentication.models import User
from ...notifications.models import Notifications
import json


class BaseTest(TestCase):

    def setUp(self):
        """ automatically run the function before running other tests"""
        self.test_client = Client()
        self.title = "hahahhaha hahaha hahah ahhah"

        self.tags = ["reactjs", "angularjs", "dragons"]
        self.article_with_tags = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tags": self.tags
            }
        }

        self.article_to_create = {
            "article": {
                "title": self.title,
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

        self.user_to_login = {
            'user': {
                'email': 'haven.authors@gmail.com',
                'password': 'jakejake@20AA'
            }
        }

        self.user_to_login2 = {
            'user': {
                'email': 'haven.authors2@gmail.com',
                'password': 'jakejake@20AA'
            }
        }

        self.rating_to_create = {
            "rating": {
                "rating": 1,
                "review": "the service was really great. I recomend you go there."
            }
        }

        self.rating_lower_than_1 = {
            "rating": {
                "rating": 0,
                "review": "the service was really great. I recomend you go there."
            }
        }

        self.rating_greater_than_5 = {
            "rating": {
                "rating": 6,
                "review": "the service was really great. I recomend you go there."
            }
        }

        self.comment_to_create = {
            "comment": {
                "body": "His name was my name too.",
            }
        }

        self.comment_as_thread_of_another = {
            "comment": {
                "body": "His name was my name too.",
                "parent_id": 1
            }
        }

        self.longer_than_8000_comment_body = {
            "comment": {
                "body": "H" * 80000,
            }
        }

        self.comment_update_greater_than_8000 = {
            "comment": {
                "body": "H" * 80000,
            }
        }

        self.child_comment_update_greater_than_8000 = {
            "comment": {
                "body": "H" * 80000,
                "parent_id": 1
            }
        }

        # this is a list of notifications to mart as read
        self.mark_as_read = {
            "notification": {
                "notifications": [1]
            }
        }

        # this is a list of notifications to mart as read
        self.mark_as_read_no_exitsent = {
            "notification": {
                "notifications": [8, 9]
            }
        }

        # Create a verified user
        self.username = 'Aurthurs'
        johndoe_user = User.objects.create_user(
            self.username, 'haven.authors@gmail.com', 'jakejake@20AA')
        johndoe_user.is_verified = True
        johndoe_user.save()

        jonedoe_user = User.objects.create_user(
            'Aurthurs2', 'haven.authors2@gmail.com', 'jakejake@20AA')
        jonedoe_user.is_verified = True
        jonedoe_user.save()

        self.user_logged_in = self.login_user(self.user_to_login)
        self.user_2_logged_in = self.login_user(self.user_to_login2)
        self.create_article = self.create_an_article(
            self.article_to_create, self.user_logged_in)
        self.own_article = self.create_an_article(
            self.article_to_create, self.user_2_logged_in)

        # create a notification for the test user
        alert = Notifications.objects.create(
            article_id=Article.objects.get(pk=1), notification_title="Title", notification_body="body",
            notification_owner=User.objects.get(pk=2),
        )
        alert.save()

        # update an article with id 1
        self.updated_article = self.update_an_article(
            self.user_logged_in
        )
        self.foloo = self.follow_a_user()

        # This creats a comment to an article using the `comment_on_article` method below
        self.article_comment = self.comment_on_article(
            self.comment_to_create)

        # This create a comment that is a threat to a parent comment
        self.thread_comment = self.comment_on_article(
            self.comment_as_thread_of_another)

        # This created a comment with body text longer than 8000 characters
        self.longer_than_8000_comment = self.comment_on_article(
            self.longer_than_8000_comment_body)

        # update a comment
        self.update_a_comment = self.update_comment(
            self.comment_to_create
        )

        # update a child comment
        self.update_child_comment = self.update_comment(
            self.comment_as_thread_of_another
        )

        # very long child comment body
        self.update_long_child_comment = self.update_comment(
            self.child_comment_update_greater_than_8000
        )

        # very long parent comment body
        self.update_long_parent_comment = self.update_comment(
            self.comment_update_greater_than_8000
        )

        # delete a comment
        self.delete_a_comment = self.delete_comment()

        # delete non_existent_comment
        self.delete_non_exitent_comment = self.delete_comment()

    def login_user(self, user_details_dict):
        """Authenticate the user credentials and login

        Args:
            user_details_dict: a dictionary with email and password of the user.

        Returns: an issued post request to the user Authentication endpoint.
        """
        return self.test_client.post(
            "/api/users/login/", data=json.dumps(user_details_dict),
            content_type='application/json')

    def create_an_article(self, article, article_owner):
        # log the user in to get auth token
        response = article_owner

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to create an article
        return self.test_client.post(
            "/api/articles/", **headers,
            data=json.dumps(article), content_type='application/json')

    def update_an_article(self, article_owner):
        # log the user in to get auth token
        response = article_owner

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to create an article
        return self.test_client.put(
            "/api/articles/1", **headers,
            data=json.dumps(self.article_to_update), content_type='application/json')

    def comment_on_article(self, comment):
        # log the user in to get auth token
        response = self.user_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to create an article
        return self.test_client.post(
            "/api/articles/1/comment/", **headers,
            data=json.dumps(comment), content_type='application/json')

    def update_comment(self, comment):
        # log the user in to get auth token
        response = self.user_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to update an article
        return self.test_client.put(
            "/api/articles/1/comment/", **headers,
            data=json.dumps(comment), content_type='application/json')

    def delete_comment(self):
        # log the user in to get auth token
        response = self.user_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        # send a request to update an article
        return self.test_client.delete(
            "/api/articles/1/comment/", **headers)

    def follow_a_user(self):
        # follow a user
        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        return self.test_client.post(
            "/api/profiles/{}/follow/".format("Aurthurs"), **headers, content_type='application/json')

    def tearDown(self):
        pass


class TestArticles(BaseTest):

    def test_create_article(self):

        response = self.create_article

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['article']['message'], 'Article created successfully.')

    def test_update_article(self):
        response = self.updated_article

        #  perform test for update on an article
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['article']['message'], 'Article updated successfully.')


class TestArticleRating(BaseTest):

    def test_create_rating(self):
        """ test if a rating can be created """
        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_to_create), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['Rating']['message'], 'Article rated successfully.')

    def test_rating_lower_than_1(self):
        """ test if a user can make rating level less than one """

        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_lower_than_1), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['rating'], ['Rating should be in range of 1 to 5.'])

    def test_rating_greater_than_5(self):
        """ test if a user can make rating level greater than five """

        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_greater_than_5), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['rating'], ['Rating should be in range of 1 to 5.'])

    def test_user_rating_twice(self):
        """  test is  a user can rate the same artricle twice """

        response = self.user_2_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_to_create), content_type='application/json')

        response2 = self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_to_create), content_type='application/json')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(
            response2.json()['errors']['error'], ['You cannot rate an article twice.'])

    def test_if_user_can_rate_own_article(self):
        """ test if a user can rate own articles """

        response = self.user_logged_in

        # extrct token from response
        token = response.json()['user']['token']

        # generate an HTTP header with token
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}

        response = self.test_client.post(
            "/api/articles/1/rating/", **headers,
            data=json.dumps(self.rating_to_create), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['error'], ['You cannot rate your own article'])


class TestCommentingOnArtilces(BaseTest):

    def test_comment_on_article(self):
        """ test if a user can create a comment """

        response = self.article_comment

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['comment']['message'], 'Comment created successfully.')

    def test_create_a_threading_comment(self):
        """ test if a comment can be created as a thread """

        response = self.thread_comment

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['comment']['message'], 'Comment created successfully.')

    def test_artcle_with_long_body(self):
        """ test if a comment body can be longer than 8000 characters """

        response = self.longer_than_8000_comment

        #  perform test case test
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['body'], [
                'A comment cannot be more than 8000 characters including spaces.'])

    def test_search_articles_by_title(self):
        """ test for a successful search for article by title"""
        response = self.test_client.get(
            "/api/articles/search?title={}".format(self.title), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_articles_by_author(self):
        """ test for a successful search for articles by author"""
        response = self.test_client.get(
            "/api/articles/search?author={}".format(self.username), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_articles_by_tag(self):
        """ test for a successful search for articles by a tag"""
        self.create_an_article(self.article_with_tags, self.user_logged_in)
        response = self.test_client.get(
            "/api/articles/search?tag={}".format(self.tags[0]), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_articles_return_with_an_empty_query_set(self):
        """ test for a successful search for articles by a non exisiting tag"""
        self.create_an_article(self.article_with_tags, self.user_logged_in)
        response = self.test_client.get(
            "/api/articles/search?tag={}".format("someraretag"), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_comment(self):
        response = self.update_a_comment

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['comment']['message'], 'Comment updated successfully.')

    def test_update_child_comment(self):
        response = self.update_child_comment

        #  perform test case test
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()['comment']['message'], 'Comment updated successfully.')

    def test_child_comment_body_long(self):
        """ test if a comment body can be longer than 8000 characters on update"""

        response = self.update_long_child_comment

        #  perform test case test
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['body'], [
                'A comment cannot be more than 8000 characters including spaces.'])

    def test_parent_comment_body_long(self):
        """ test if a comment body can be longer than 8000 characters on update"""

        response = self.update_long_parent_comment

        #  perform test case test
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['errors']['body'], [
                'A comment cannot be more than 8000 characters including spaces.'])

    def test_delete_comment(self):
        """ test if a comment body can be longer than 8000 characters on update"""

        response = self.delete_a_comment

        #  perform test case test
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['comment']['message'], 'Comment deleted succesfully.')

    def test_delete_non_existing_comment(self):
        response = self.delete_non_exitent_comment

        #  perform test case test
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()['comment']['error'], 'The comment id was not found')
