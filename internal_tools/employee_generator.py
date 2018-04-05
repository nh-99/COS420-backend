#!/usr/bin/python3
# Simple CLI tool to generate employees

from cos420_backend.models import Employee
import cos420_backend.models as models

session = models.DBSession

role = input('Enter role: ')
street_address = input('Enter street address: ')
city = input('Enter city: ')
state = input('Enter state: ')
payroll_type = input('Enter payroll type: ')
wage_type = input('Enter wage type: ')
rate = input('Enter rate: ')

employee = Employee(
    role = role,
    street_address = street_address,
    city = city,
    state = state,
    payroll_type = payroll_type,
    wage_type = wage_type,
    rate = int(rate),
    overtime = False,
    overtime_rate = 0,
    is_active = True
)

session.add(employee)
session.commit()
