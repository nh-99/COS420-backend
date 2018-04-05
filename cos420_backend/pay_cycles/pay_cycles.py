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
from cos420_backend.models import PayCycle


"""
Return pay cycle info
"""
class PayCycleResource(object):

    @staticmethod
    def on_get(req, resp, id):
        cycle = PayCycle.query.filter_by(id=uuid.UUID(id)).first()
        resp.body = json.dumps(cycle.serialize)
