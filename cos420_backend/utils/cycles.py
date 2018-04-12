"""
Manipulation & querying of pay cycle objects
"""
from cos420_backend.models import PayCycle, Employee
from uuid import UUID


def get_latest_cycle(employee_id, company_id):
    cycle = PayCycle.query.filter_by(employee_id=employee_id, company_id=company_id).order_by('time_created desc').first()
    return cycle
