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
        except Exception as e:
            return "invalid token"


class Mailer:
    """Sends emails to users"""

    # SMTP configuration values
    host_domain = os.getenv('HOST_DOMAIN')
    sender_domain = os.getenv('EMAIL_HOST')
    sender_port = os.getenv('EMAIL_PORT')
    sender_email = os.getenv('EMAIL_HOST_USER')
    sender_password = os.getenv('EMAIL_HOST_PASSWORD')

    # SMTP connection
    server = smtplib.SMTP("{}:{}".format(sender_domain, sender_port))
    server.ehlo()
    server.starttls()
    server.login(sender_email, sender_password)

    # https://stackoverflow.com/questions/8022530/python-check-for-valid-email-address/8022584
    # validate and verify that the email does exist and is reachable
    # validate that the email address's domain is also available
    @staticmethod
    def verify_email_exists(email_address):
        if validate_email(email_address, check_mx=True) is False:
            return False
        else:
            return True

    def copyright_year(self):
        """ returns the current year expressed as a string"""

        return datetime.strftime(datetime.now(), "%Y")

    # https://github.com/abulojoshua1/ipt/blob/master/sendmail.py
    def send(self, user, email_subject, template_name, context):

        # Add more values to render in the template
        context['copyright_year'] = self.copyright_year()
        context['domain'] = self.host_domain

        # Load and return the verify_email template
        template = loader.get_template(template_name)

        # header attached to the email
        headers = "\r\n".join(["from: " + self.sender_email,
                               "subject: " + email_subject,
                               "to: " + user['email'],
                               "mime-version: 1.0",
                               "content-type: text/html"])

        # body_of_email can be plaintext or html!
        content = headers + "\r\n\r\n" + template.render(context)

        # Send an email
        self.server.sendmail(self.sender_email, user['email'], content)
