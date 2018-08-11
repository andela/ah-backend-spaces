from .base import BaseTest, json


class LikeArticleTest(BaseTest):
    def test_getting_articles(self):
        """ test a user can get all likes """

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.get(
            "/api/articles/1/", **auth_headers, content_type='application/json')

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.json()['article']['error'], "method GET not allowed")

    def test_liking_articles(self):
        """ test a user can like an article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_like_un_known_article(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1000/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_like_article_twice(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        # like article 1 the first time
        self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        # like article 1 the second time
        response = self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_like_article_with_null(self):

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.null_article_to_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_update_like(self):
        """ test a user can like an article with a dislike"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        response = self.test_client.put(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_can_update_like_on_un_liked_article(self):
        """ test a user can like any article with a dislike"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.put(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_update_like_on_un_known_article(self):
        """ test a user can like any article with a dislike"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        response = self.test_client.put(
            "/api/articles/10000/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_delete_like(self):
        """ test a user can delete an like on an article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        self.test_client.post(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_like), content_type='application/json')

        response = self.test_client.delete(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_can_delete_like_on_unliked_article(self):
        """ test a user can delete an like on any article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        # send a request to create an article
        self.test_client.post(
            "/api/articles/", **auth_headers,
            data=json.dumps(self.article_to_create), content_type='application/json')

        response = self.test_client.delete(
            "/api/articles/1/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_can_delete_like_on_un_known_article(self):
        """ test a user can delete an like on an unknown article"""

        # log the user in to get auth token
        auth_headers = self.user_logged_in

        response = self.test_client.delete(
            "/api/articles/1000/", **auth_headers,
            data=json.dumps(self.article_to_dis_like), content_type='application/json')

        self.assertEqual(response.status_code, 400)
