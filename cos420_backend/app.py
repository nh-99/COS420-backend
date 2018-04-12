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
from cos420_backend.company.company import CompanyResource
from cos420_backend.employee.employee import EmployeeResource
from cos420_backend.pay_cycles.pay_cycles import PayCycleResource
from cos420_backend.hours.hours import HoursResource, ReportHoursResource, SubmitHoursResource

import cos420_backend.settings as settings
from cos420_backend.models import User


# User token authenciation method. If we have a decrypted payload, that means
# that the token is valid, so we can just return the user object from the
# payload. Otherwise, we return None for a nice fail message.
def auth_user(payload):
    try:
        user = payload['user']
        return user
    except KeyError:
        return None

# Auth handler
auth_backend = JWTAuthBackend(auth_user, settings.SECRET_KEY, expiration_delta=2 * 60 * 60)
auth_middleware = FalconAuthMiddleware(auth_backend)


# Create resources
auth_resource = AuthResource(auth_backend)

user_resource = UserResource()

company_resource = CompanyResource()

employee_resource = EmployeeResource()

pay_cycle_resource = PayCycleResource()
report_hours_resource = ReportHoursResource()

hours_resource = HoursResource()
submit_hours_resource = SubmitHoursResource()


# Create falcon app
app = falcon.API(middleware=[auth_middleware])

# User routes
app.add_route('/users/login', auth_resource)
app.add_route('/users/me', user_resource)

# Company routes
app.add_route('/company/{id}', company_resource)

# Employee routes
app.add_route('/employee/{id}', employee_resource)

# Pay cycle routes
app.add_route('/cycle/{id}', pay_cycle_resource)

# Hours routes
app.add_route('/hours/report', report_hours_resource)
app.add_route('/hours/{id}', hours_resource)
app.add_route('/hours/submit', submit_hours_resource)


# Useful for debugging problems in API, it works with pdb
if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
