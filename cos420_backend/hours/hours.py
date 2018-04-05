# -*- coding: utf-8 -*-
"""
Hours resource. Returns info about hours.
"""
# System imports
import json, uuid
import datetime
from datetime import timedelta

# Third-party imports
import falcon
import intervals
from falcon_auth import BasicAuthBackend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from cos420_backend import settings
from cos420_backend.models import Hours, Employee
import cos420_backend.models as models
import cos420_backend.utils.users as users
import cos420_backend.utils.cycles as cycles


"""
Return hours info
"""
class HoursResource(object):

    @staticmethod
    def on_get(req, resp, id):
        hours = Hours.query.filter_by(id=uuid.UUID(id)).first()
        if hours:
            resp.body = json.dumps(hours.serialize)
        else:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Hours with given ID do not exist'})


"""
Enables the reporting and tracking of employee hours.
"""
class ReportHoursResource(object):

    @staticmethod
    def on_post(req, resp):
        raw_json = req.stream.read().decode('utf-8')
        data = json.loads(raw_json, encoding='utf-8')

        # Get data from request
        user_id = req.context['user']['id']
        company_id = data.get('company_id')

        # Convert times into datetime objects and get timedelta
        start_time = datetime.datetime.fromtimestamp(int(data.get('start')))
        end_time = datetime.datetime.fromtimestamp(int(data.get('end')))
        time_diff = (end_time - start_time) / timedelta(hours=1)

        # Check if the user is in the specified company
        employee_id = users.user_in_company(user_id, company_id)
        if not employee_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'User is not a part of the company'})
            # TODO: return to finsh the request?
            return

        # Get the employee object from the database to assign the current pay cycle to the hours object
        pay_cycle = cycles.get_latest_cycle(employee_id, company_id)

        # Check if hours are out of pay cycle and return an error
        if not pay_cycle.time_range.__and__(intervals.DateTimeInterval([start_time, end_time])):
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'Hours are not within the current pay cycle'})
            # TODO: return to finsh the request?
            return

        # Check if hours overlap and return an error
        hours = Hours.query.filter_by(pay_cycle_id=pay_cycle.id).all()
        exists = False
        # Scan through all hours in current pay cycle and see if we've already
        # logged time for them
        for hour in hours:
            if hour.time_range.__and__(intervals.DateTimeInterval([start_time, end_time])):
                exists = True
        if exists:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'These hours are already recorded'})
            # TODO: return to finsh the request?
            return

        # Checks pass, create our object and return a valid response
        hours = Hours(time_range=intervals.DateTimeInterval([start_time, end_time]), total_hours=time_diff, pay_cycle_id=pay_cycle.id, approved=False)
        hours.pay_cycle = pay_cycle # Add pay cycle to hours object
        models.DBSession.add(hours) # Commit hours to database
        models.DBSession.commit()
        resp.body = json.dumps(hours.serialize) # Return serialized version of the hours object
