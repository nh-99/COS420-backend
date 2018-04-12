# -*- coding: utf-8 -*-
"""
Company resource. Returns info about companies.
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
from cos420_backend.models import Company, User
import cos420_backend.utils.static as static


"""
Return company info
"""
class CompanyResource(object):

    @staticmethod
    def on_get(req, resp, id):
        # Find the company
        company = Company.query.filter_by(id=id).first()

        # Find the user
        user_id = req.context['user']['id']
        user = User.query.filter_by(id=user_id).first()
        user_in_company = False

        # Check if the any of the user's employee objects are in the company
        for employee in user.employee:
            if employee.company_id == company.id:
                user_in_company = True

        # If the company isn't found, give a 404
        if not company:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Company with given ID found'})

        # If the user isn't in the company, give an unauthorized error
        if not user_in_company:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must be a part of the company to get info about it'})

        # All checks pass, so return the company
        if employee.role == static.ADMIN_ROLE or employee.role == static.ACCOUNTANT_ROLE:
            resp.body = json.dumps(company.serialize_owner)
        else:
            resp.body = json.dumps(company.serialize)
