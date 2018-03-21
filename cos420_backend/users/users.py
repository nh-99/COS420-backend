# -*- coding: utf-8 -*-
"""
User resource. Stores info about the user and handles authentication.
"""
# System imports
import json
# Third-party imports
import falcon
from falcon_auth import BasicAuthBackend

# Local imports
from cos420_backend import settings


"""
Class to authenticate the user with basic auth and return a token
"""
class AuthResource:
    auth = {
        'backend': BasicAuthBackend(user_loader=lambda username, password: { 'username': username })
    }

    def __init__(self, auth_backend):
        self.auth_backend = auth_backend

    def on_post(self, req, resp):
        resp.body = json.dumps({'token': self.auth_backend.get_auth_token(req.context['user'])})


"""
Return user profile
"""
class UserResource(object):
    """ Just a sample resource model to
    test the falcon app"""

    @staticmethod
    def on_get(req, resp):
        user = req.context['user']
        resp.body = "User Found: {}".format(user['username'])
