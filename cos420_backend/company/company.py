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
from cos420_backend.models import Company


"""
Return company info
"""
class CompanyResource(object):

    @staticmethod
    def on_get(req, resp, id):
        company = Company.query.filter_by(id=uuid.UUID(id)).first()
        if company:
            resp.body = json.dumps(company.serialize)
        else:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Company with given ID found'})
