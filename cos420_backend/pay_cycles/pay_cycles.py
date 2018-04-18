# -*- coding: utf-8 -*-
"""
Pay cycle resource. Returns info about employees.
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
from cos420_backend.models import PayCycle, Employee
import cos420_backend.utils.users as users
import cos420_backend.utils.cycles as cycles
import cos420_backend.utils.employee as employees
import cos420_backend.utils.static as static


"""
Return pay cycle info
"""
class PayCycleResource(object):

    @staticmethod
    def on_get(req, resp, employee_id):
        data = req.params
        user_id = req.context['user']['id']
        company_id = data.get('company_id', None)
        empl_id = users.user_in_company(user_id, company_id)
        employee = None
        print('gettin')

        # Check that a user id is supplied
        if not user_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must supply a user ID in the query string'})
            return

        # Check that a company id is supplied
        if not company_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must supply a company ID in the query string'})
            return

        # Check if employee has the admin role
        employee = Employee.query.filter_by(id=empl_id).first()
        if employee.role != static.ADMIN_ROLE and employee.role != static.ACCOUNTANT_ROLE:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You do not have access to this users cycles.'})
            return

        # Check if the employee was found in the specified company
        employee = employees.employee_in_company(employee_id, company_id)
        if not employee:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'Employee is not a part of the company'})
            return

        # All of the initial checks pass, find and return the cycle to the user
        cycle = cycles.get_latest_cycle(employee_id, company_id)

        if not cycle:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'No pay cycle found for the specified employee'})
            return

        resp.body = json.dumps(cycle.serialize)

"""
Return info on the current pay cycle for the signed in user
"""
class CurrentPayCycleResource(object):

    @staticmethod
    def on_get(req, resp):
        data = req.params
        user_id = req.context['user']['id']
        company_id = data.get('company_id', None)
        employee_id = users.user_in_company(user_id, company_id)
        employee = None
        print('gettin')

        # Check that a user id is supplied
        if not user_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must supply a user ID in the query string'})
            return

        # Check that a company id is supplied
        if not company_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must supply a company ID in the query string'})
            return

        # Check if the employee was found in the specified company
        if not employee_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'User is not a part of the company'})
            return

        # All of the initial checks pass, find and return the cycle to the user
        cycle = cycles.get_latest_cycle(employee_id, company_id)

        if not cycle:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'No pay cycle found for the specified employee'})
            return

        resp.body = json.dumps(cycle.serialize)
