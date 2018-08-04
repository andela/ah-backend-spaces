# import facebook library
import facebook


class FacebookValidate:

    @staticmethod
    def validate(auth_token):
        try:
            # create an instance of the facebook
            graph = facebook.GraphAPI(access_token=auth_token, version="2.7")

            # fetch user info i.e. name, email and picture
            profile = graph.request('/me?fields=id,name,email,picture')
            return profile
        except:  # noqa: E722
            msg = "The token is either invalid or expired."
            return msg
