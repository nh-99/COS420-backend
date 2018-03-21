# -*- coding: utf-8 -*-
"""
App runner
"""
# System imports
# Third-party imports
import falcon
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend

# Local imports
from cos420_backend.users.users import AuthResource, UserResource
import cos420_backend.settings as settings

# Auth handler
user_loader = lambda username: { 'username': username }
auth_backend = JWTAuthBackend(user_loader, settings.SECRET_KEY)
auth_middleware = FalconAuthMiddleware(auth_backend)


# Create resources
auth_resource = AuthResource(auth_backend)
user_resource = UserResource()


# Create falcon app
app = falcon.API(middleware=[auth_middleware])
app.add_route('/users/login', auth_resource)
app.add_route('/users/me', user_resource)


# Useful for debugging problems in API, it works with pdb
if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
