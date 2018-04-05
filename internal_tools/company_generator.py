#!/usr/bin/python3
# Simple CLI tool to generate companies

from cos420_backend.models import Company
import cos420_backend.models as models

session = models.DBSession

name = input('Enter your company name: ')
street_address = input('Enter your address: ')
city = input('Enter your city: ')
state = input('Enter your state: ')

company = Company(
    name=name,
    street_address=street_address,
    city=city,
    state=state
)
session.add(company)
session.commit()

print('Company created. ID: ' + str(company.id))
