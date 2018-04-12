"""
"""
from cos420_backend.models import PayCycle
import cos420_backend.models as models

def get_hours_approved(pay_cycle_id):
    to_return = True
    pay_cycle = PayCycle.query.filter_by(id=pay_cycle_id).first()

    # Loop through hours and see if any of them aren't approved
    for hour in pay_cycle.hours:
        if hour.approved == False:
            to_return = False
    return to_return
