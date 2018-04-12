# -*- coding: utf-8 -*-
"""
User resource. Stores info about the user and handles authentication.
"""
# System imports
import json

# Third-party imports
import falcon
from falcon_auth import BasicAuthBackend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from cos420_backend import settings
from cos420_backend.models import User

# Method to be used for authenticating the user.
# Returns the serialized user if authentication passes, otherwise returns None
def auth_user(username, password):
    user = User.query.filter_by(email=username).first()
    if user and user.verify_password(password):
        return user.serialize
    else:
        return None

"""
Class to authenticate the user with basic auth and return a token
"""
class AuthResource:
    auth = {
        'backend': BasicAuthBackend(user_loader=auth_user)
    }

    def __init__(self, auth_backend):
        self.auth_backend = auth_backend


    def on_post(self, req, resp):
        resp.body = json.dumps({'token': self.auth_backend.get_auth_token(req.context['user'])})



"""
Return user profile
"""
class UserResource(object):

    @staticmethod
    def on_get(req, resp):
        user = req.context['user']
        resp.body = "User Found: {}".format(user['email'])
