import os
import smtplib
from datetime import datetime, timedelta
from validate_email import validate_email
from django.template import loader

import jwt
from django.conf import settings


class TokenGenerator:
    """
    Generates custom tokens used in verifying users and password reseting
    """

    def make_custom_token(self, details_dict):
        """ Generates a custom token using jwt

        Args:
            **details_dict: a dictionary containing the values to be encoded

        Returns: returns an encrypted token
        """

        return jwt.encode(
            details_dict, settings.SECRET_KEY, algorithm='HS256'
        ).decode('utf-8')

    def decode_token(self, token):
        """ decodes a token using jwt

        Args:
            token: an encoded token containing the values to be decoded

        Returns: returns a dictionary with decoded values
        """
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')
        except Exception:
            return "invalid token"


class Mailer:
    """Mailer is used to emails to users"""

    # SMTP configuration values
    host_domain = os.getenv('HOST_DOMAIN')
    sender_domain = os.getenv('EMAIL_HOST')
    sender_port = os.getenv('EMAIL_PORT')
    sender_email = os.getenv('EMAIL_HOST_USER')
    sender_password = os.getenv('EMAIL_HOST_PASSWORD')

    def __init__(self):
        self._server = self.get_smtp_connection()

    def get_smtp_connection(self):
        server = smtplib.SMTP(self.sender_domain)
        server.ehlo()
        server.starttls()
        return server

    @property
    def server(self):
        return self._server

    # https://stackoverflow.com/questions/8022530/python-check-for-valid-email-address/8022584
    # validate that the email address's domain is also available
    @staticmethod
    def verify_email_exists(email_address):
        if validate_email(email_address, check_mx=True) is False:
            return False
        else:
            return True

    def get_copyright_year(self):
        """ returns the current year expressed as a string"""

        return datetime.strftime(datetime.now(), "%Y")

    # https://github.com/abulojoshua1/ipt/blob/master/sendmail.py
    def send(self, user_email, email_subject, template_name, context):

        # Add more values to render in the template
        context['copyright_year'] = self.get_copyright_year()
        context['domain'] = self.host_domain

        # Load and return the verify_email template
        template = loader.get_template(template_name)

        # header attached to the email
        headers = "\r\n".join(["from: " + self.sender_email,
                               "subject: " + email_subject,
                               "to: " + user_email,
                               "mime-version: 1.0",
                               "content-type: text/html"])

        # body_of_email can be plaintext or html!
        content = headers + "\r\n\r\n" + template.render(context)

        # Send an email if smtp server connection exists
        if self.get_smtp_connection() is not False:
            self.server.login(self.sender_email, self.sender_password)
            self.server.sendmail(self.sender_email, user_email, content)
            self.server.quit()
            return True
        return False
