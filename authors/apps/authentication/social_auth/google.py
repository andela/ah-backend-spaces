from google.oauth2 import id_token
from google.auth.transport import requests
import os

# (Receive token by HTTPS POST)
# ...


class google_auth:

    @staticmethod
    def validate(auth_token):
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            return idinfo
        except ValueError:
            # if token is Invalid token
            return "The token is either invalid or expired."
