from dataclasses import dataclass


@dataclass
class EmployeeInfoQuery:
    employee_name: str
    field: str
