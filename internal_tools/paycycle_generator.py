#!/usr/bin/python3
# Simple CLI tool to generate employees

from datetime import datetime, timedelta
from cos420_backend.models import PayCycle
import cos420_backend.models as models
from uuid import UUID
import intervals

session = models.DBSession

start = datetime.utcnow() - timedelta(days=30)
end = datetime.utcnow() + timedelta(days=30)

cycle = PayCycle(
    employee_id='0ca4150b-740d-4441-a511-3b80d2bc1366',
    company_id='b824f8f2-e9c6-4ae4-a4cb-377ff52e4fef',
    time_range=intervals.DateTimeInterval([start, end])
)

session.add(cycle)
session.commit()
