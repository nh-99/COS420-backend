# -*- coding: utf-8 -*-
"""
Employee resource. Returns info about employees.
"""
# System imports
import json, uuid

# Third-party imports
import falcon
from falcon_auth import BasicAuthBackend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from cos420_backend import settings
from cos420_backend.models import Employee


"""
Return employee info
"""
class EmployeeResource(object):

    @staticmethod
    def on_get(req, resp, id):
        employee = Employee.query.filter_by(id=uuid.UUID(id)).first()
        if employee:
            resp.body = json.dumps(employee.serialize)
        else:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Employee with given ID not found'})
