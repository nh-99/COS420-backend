"""
This class contains helper methods for manipulating employees. It's mainly used
for checking certain things on API routes.
"""
from cos420_backend.models import Employee, Company


# Checks if a user is in a company
def employee_in_company(employee_id, company_id):
    employee = Employee.query.filter_by(id=employee_id).first()

    if str(employee.company_id) == str(company_id):
        return employee

    return False
