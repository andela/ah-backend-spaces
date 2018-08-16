from rest_framework.exceptions import APIException


class ArticlesNotExist(APIException):
    status_code = 400
    default_detail = 'you have no articles'
