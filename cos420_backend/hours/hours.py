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
from bson import json_util
from falcon_auth import BasicAuthBackend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from cos420_backend import settings
from cos420_backend.models import Hours, Employee, PayCycle, Company
import cos420_backend.models as models
import cos420_backend.utils.users as users
import cos420_backend.utils.cycles as cycles
import cos420_backend.utils.static as static


"""
Return hours info
"""
class HoursResource(object):

    @staticmethod
    def on_get(req, resp, id):
        data = req.params
        user_id = req.context['user']['id']
        employee_id = data.get('employee_id', None)
        company_id = data.get('company_id', None)
        employee_id = users.user_in_company(user_id, company_id)
        employee = None

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

        hours = Hours.query.filter_by(id=uuid.UUID(id)).first()
        pay_cycle = PayCycle.query.filter_by(id=hours.pay_cycle_id).first()
        if hours:
            if employee_id != pay_cycle.employee_id:
                if employee.role != static.ADMIN_ROLE and employee.role != static.ACCOUNTANT_ROLE:
                    resp.status = falcon.HTTP_403
                    resp.body = json.dumps({'error': 'You do not have access to see these hours'})
                    return

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
            return
        employee = Employee.query.filter_by(id=employee_id).first()

        if not employee.is_active:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You are not an active employee in the company'})
            return

        # Get the employee object from the database to assign the current pay cycle to the hours object
        pay_cycle = cycles.get_latest_cycle(employee_id, company_id)

        # Check if hours are out of pay cycle and return an error
        if not intervals.DateTimeInterval([start_time, end_time]) in pay_cycle.time_range:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'Hours are not within the current pay cycle'})
            return

        # Check if hours overlap and return an error
        hours = Hours.query.filter_by(pay_cycle_id=pay_cycle.id).all()
        exists = False
        # Scan through all hours in current pay cycle and see if we've already
        # logged time for them
        for hour in hours:
            if intervals.DateTimeInterval([start_time, end_time]) in hour.time_range:
                exists = True
        if exists:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'These hours are already recorded'})
            return

        # Checks pass, create our object and return a valid response
        hours = Hours(time_range=intervals.DateTimeInterval([start_time, end_time]), total_hours=time_diff, pay_cycle_id=pay_cycle.id, approved=False)
        hours.pay_cycle = pay_cycle # Add pay cycle to hours object
        models.DBSession.add(hours) # Commit hours to database
        models.DBSession.commit()
        resp.body = json.dumps(hours.serialize) # Return serialized version of the hours object

    @staticmethod
    def on_delete(req, resp):
        raw_json = req.stream.read().decode('utf-8')
        data = json.loads(raw_json, encoding='utf-8')

        user_id = req.context['user']['id']
        company_id = data.get('company_id')
        hours_id = data.get('hours_id')
        employee_id = users.user_in_company(user_id, company_id)
        employee = None

        # Check if the employee was found in the specified company
        if not employee_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'User is not a part of the company'})
            return

        # Check if employee has the admin role
        employee = Employee.query.filter_by(id=employee_id).first()
        if employee.role != static.ADMIN_ROLE:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You do not have access to delete these hours'})
            return

        # All checks pass, so delete the hours object
        hours = Hours.query.filter_by(id=hours_id).first()
        if not hours:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Hours with specified ID not found'})
            return

        models.DBSession.delete(hours)
        models.DBSession.commit()

        resp.body = json.dumps({'msg': 'Hours deleted successfully.'})

    @staticmethod
    def on_put(req, resp):
        raw_json = req.stream.read().decode('utf-8')
        data = json.loads(raw_json, encoding='utf-8')

        user_id = req.context['user']['id']
        company_id = data.get('company_id')
        hours_id = data.get('hours_id')
        to_update = data.get('fields')
        employee_id = users.user_in_company(user_id, company_id)
        employee = None

        # Check if the employee was found in the specified company
        if not employee_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'User is not a part of the company'})
            return

        # Check if employee has the admin role
        employee = Employee.query.filter_by(id=employee_id).first()
        if employee.role != static.ADMIN_ROLE and employee.role != static.ACCOUNTANT_ROLE:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You do not have access to update these hours'})
            return

        # All checks pass, so update the hours object
        hours = Hours.query.filter_by(id=hours_id).first()
        if not hours:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'error': 'Hours with specified ID not found'})
            return

        # Try to update either time range or approval
        if to_update.get('start', None) != None and to_update.get('end', None) != None:
            hours.time_range = intervals.DateTimeInterval([to_update['start'], to_update['end']])
            time_diff = (end_time - start_time) / timedelta(hours=1)
            hours.total_hours = time_diff
        if to_update.get('approved', None) != None:
            hours.approved = to_update.get('approved', False)

        models.DBSession.add(hours)
        models.DBSession.commit()

        resp.body = json.dumps({'msg': 'Hours updated successfully.'})


"""
Submit hours for a company
"""
class SubmitHoursResource(object):

    @staticmethod
    def on_post(req, resp):
        raw_json = req.stream.read().decode('utf-8')
        data = json.loads(raw_json, encoding='utf-8')

        user_id = req.context['user']['id']
        company_id = data.get('company_id', None)
        employee_id = users.user_in_company(user_id, company_id)
        employee = None

        # Check that a company id is supplied
        if not company_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You must supply a company ID'})
            return

        # Check if the employee was found in the specified company
        if not employee_id:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'User is not a part of the company'})
            return

        # Check if employee has the admin role
        employee = Employee.query.filter_by(id=employee_id).first()
        if employee.role != static.ADMIN_ROLE and employee.role != static.ACCOUNTANT_ROLE:
            resp.status = falcon.HTTP_403
            resp.body = json.dumps({'error': 'You do not have access to see these hours'})
            return

        company = Company.query.filter_by(id=company_id).first()

        # Loop through all employees and give them a fresh, new pay cycle
        for employee_tp in company.employees:
            # Get the employee object from the database to assign the current pay cycle to the hours object
            pay_cycle = cycles.get_latest_cycle(employee_tp.id, company_id)

            # Get the end of the last cycle, and add 1 second to get the start of our new cycle
            new_start = pay_cycle.time_range.upper + timedelta(seconds=1)
            new_end = new_start + (pay_cycle.time_range.upper - pay_cycle.time_range.lower) - timedelta(seconds=1)

            pay_cycle = PayCycle(
                employee_id=employee_tp.id,
                company_id=company.id,
                time_range=intervals.DateTimeInterval([new_start, new_end])
            )
            models.DBSession.add(pay_cycle)

        models.DBSession.commit()
        resp.body = json.dumps({'msg': 'Payroll has been submitted successfully'})
