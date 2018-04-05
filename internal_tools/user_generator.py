#!/usr/bin/python3
# Simple CLI tool to generate users

from cos420_backend.models import User
import cos420_backend.models as models

session = models.DBSession

first_name = input('Enter your first name: ')
last_name = input('Enter your last name: ')
email = input('Enter your email address: ')
password = input('Enter your password: ')
pass_conf = input('Confirm your password: ')
print('#'*40)
security_question = input('Enter a security question: ')
security_answer = input('Your answer to the question: ')

user = User(
    first_name=first_name,
    last_name=last_name,
    email=email,
    security_question=security_question,
    security_answer=security_answer
)
user.hash_password(password)
session.add(user)
session.commit()
