from .base import BaseTest, json


class FavouriteArticleTest(BaseTest):

    def test_favouriting_articles(self):
        """ test a user can favourite an article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_favouriting_articles_with_false(self):
        """ test a user can favourite an article with false"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite_with_false),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_favourite_un_known_article(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1000/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_favourite_article_twice(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        # favourite article 1 the first time
        self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        # favourite article 1 the second time
        response = self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_favourite_article_with_null(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.null_article_to_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_delete_favourite(self):
        """ test a user can un favourite a favourite article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        response = self.test_client.delete(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_un_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_can_un_favourite_with_true(self):
        """ test a user can un favourite a favourite article with true"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        self.test_client.post(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_favourite), content_type='application/json')

        response = self.test_client.delete(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_un_favourite_with_true),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_un_favourite_an_un_favourite_article(self):
        """ test a user can delete an favourite on any article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.delete(
            "/api/articles/1/favourite/", **auth_headers,
            data=json.dumps(self.article_to_un_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_un_favourite_an_un_known_article(self):
        """ test a user can delete an like on an unknown article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        response = self.test_client.delete(
            "/api/articles/1000/favourite/", **auth_headers,
            data=json.dumps(self.article_to_un_favourite), content_type='application/json')

        self.assertEqual(response.status_code, 400)
