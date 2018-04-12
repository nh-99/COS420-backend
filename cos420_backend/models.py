# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Table, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy_utils import UUIDType, DateTimeRangeType
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from passlib.apps import custom_app_context as pwd_context

import uuid, datetime, os

Base = declarative_base()
DBSession = scoped_session(sessionmaker())

# Stores user related data in the database
class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(35))
    middle_name = Column(String(35))
    last_name = Column(String(35))
    email = Column(String(254), unique=False)
    password = Column(String(200))
    security_question = Column(String(100))
    security_answer = Column(String(50))
    employee = relationship('Employee')
    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def serialize(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }


class Company(Base):
    __tablename__ = 'company'
    query = DBSession.query_property()

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    street_address = Column(String(128))
    city = Column(String(64))
    state = Column(String(64))
    employees = relationship('Employee')

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'address': self.street_address + ', ' + self.city + ' ' + self.state,
            'employees': [User.query.filter_by(id=e.user_id).first().get_full_name() for e in self.employees]
        }

    @property
    def serialize_owner(self):
        import cos420_backend.utils.hours as hours
        import cos420_backend.utils.cycles as cycles

        return {
            'id': str(self.id),
            'name': self.name,
            'address': self.street_address + ', ' + self.city + ' ' + self.state,
            'employees': [
                {
                    'id': str(e.id),
                    'name': User.query.filter_by(id=e.user_id).first().get_full_name(),
                    'hours_approved': hours.get_hours_approved(cycles.get_latest_cycle(e.id, self.id).id)
                } for e in self.employees
            ]
        }


class Employee(Base):
    __tablename__ = 'employee'
    query = DBSession.query_property()

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(binary=False), ForeignKey('users.id'))
    company_id = Column(UUIDType(binary=False), ForeignKey('company.id'))
    role = Column(Integer) # Owner: 999
    street_address = Column(String(128))
    city = Column(String(64))
    state = Column(String(64))
    payroll_type = Column(Integer)
    wage_type = Column(String(32))
    rate = Column(Integer)
    overtime = Column(Boolean, default=False)
    overtime_rate = Column(Integer)
    pay_cycles = relationship('PayCycle')
    is_active = Column(Boolean) # Whether or not the employee is still able to log hours

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': str(self.id),
            'role': self.role,
            'address': self.street_address + ', ' + self.city + ' ' + self.state,
            'payroll_type': self.payroll_type,
            'wage_type': self.wage_type,
            'rate': self.rate / 100,
            'overtime': self.overtime,
            'overtime_rate': self.overtime_rate,
            'active': self.is_active
        }


class PayCycle(Base):
    __tablename__ = 'pay_cycle'
    query = DBSession.query_property()

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUIDType(binary=False), ForeignKey('employee.id'))
    company_id = Column(UUIDType(binary=False), ForeignKey('company.id'))
    hours = relationship('Hours')
    time_range = Column(DateTimeRangeType)
    employees = relationship('Employee')

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'hours': [h.serialize for h in self.hours],
            'time_range': self.time_range
        }


class Hours(Base):
    __tablename__ = 'hours'
    query = DBSession.query_property()

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    pay_cycle_id = Column(UUIDType(binary=False), ForeignKey('pay_cycle.id'))
    time_range = Column(DateTimeRangeType)
    approved = Column(Boolean)
    total_hours = Column(Float)

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': str(self.id),
            'total': self.total_hours,
            'start': self.time_range.lower.isoformat(),
            'end': self.time_range.upper.isoformat()
        }

from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://bangor_payroll:payroll@localhost/bangor_payroll')
DBSession.configure(bind=engine)


if __name__ == '__main__':
    db_name = 'bangor_payroll.sqlite'
    if os.path.exists(db_name):
        os.remove(db_name)

    from sqlalchemy import create_engine
    engine = create_engine('postgresql+psycopg2://bangor_payroll:payroll@localhost/bangor_payroll')
    Base.metadata.create_all(engine, checkfirst=True)
