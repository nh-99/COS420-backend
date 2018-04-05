"""
This class contains helper methods for manipulating users. It's mainly used
for checking certain things on API routes, such as roles of users.
"""
from cos420_backend.models import User, Company


# Checks if a user is in a company
def user_in_company(user_id, company_id):
    user = User.query.filter_by(id=user_id).first()

    for employee in user.employee:
        if str(employee.company_id) == str(company_id):
            return employee.id

    return False
