from .base import BaseTest, json


class ArticlePaginationTest(BaseTest):
    def test_pagination_on_user_article(self):
        """ test pageination on getting authenticated user articles"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create),
            content_type='application/json')

        response = self.test_client.get(
            "/api/articles/me/", **auth_headers,
            content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_on_user_article(self):
        """ test pageination on getting authenticated user articles"""
        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create),
            content_type='application/json')

        self.test_client.put(
            "/api/articles/1", **auth_headers,
            data=json.dumps(self.article_to_update),
            content_type='application/json')

        response = self.test_client.get(
            "/api/articles/me/", **auth_headers,
            content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['articles']['count'], 1)
        self.assertEqual(response.json()['articles']['next'], None)

    def test_any_user_gets_pagination(self):
        """ test pageination on getting all articles"""
        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create),
            content_type='application/json')

        self.test_client.put(
            "/api/articles/1", **auth_headers,
            data=json.dumps(self.article_to_update),
            content_type='application/json')

        response = self.test_client.get(
            "/api/articles/all/", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['articles']['count'], 1)
        self.assertEqual(response.json()['articles']['next'], None)

    def test_no_pagination_articles(self):
        """test 400 when no articles are published"""
        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create),
            content_type='application/json')

        response = self.test_client.get(
            "/api/articles/all/", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['articles']['detail'], "you have no articles")
