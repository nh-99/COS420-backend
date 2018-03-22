# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Table, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy_utils import UUIDType
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

    id = Column(UUIDType(binary=False), primary_key=True)
    name = Column(String(100))
    street_address = Column(String(128))
    city = Column(String(64))
    state = Column(String(64))
    default_pay_cycle = relationship('PayCycle')
    employees = relationship('Employee')

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.street_address + ', ' + self.city + ' ' + self.state,
            'pay_cycle': self.default_pay_cycle.serialize
        }


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(UUIDType(binary=False), primary_key=True)
    user_id = Column(UUIDType(binary=False), ForeignKey('users.id'))
    company_id = Column(UUIDType(binary=False), ForeignKey('company.id'))
    role = Column(Integer)
    street_address = Column(String(128))
    city = Column(String(64))
    state = Column(String(64))
    payroll_type = Column(Integer)
    wage_type = Column(String(32))
    rate = Column(Integer)
    overtime = Column(Boolean, default=False)
    overtime_rate = Column(Integer)
    is_active = Column(Boolean) # Whether or not the employee is still able to log hours
    pay_cycle = relationship('PayCycle')

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'role': self.role,
            'address': self.street_address + ', ' + self.city + ' ' + self.state,
            'payroll_type': self.payroll_type,
            'wage_type': self.wage_type,
            'rate': self.rate / 100,
            'overtime': self.overtime,
            'overtime_rate': self.overtime_rate,
            'active': self.is_active,
            'pay_cycle': self.pay_cycle.serialize
        }


paycycle_hours = Table(
    "paycycle_hours",
    Base.metadata,
    Column("fk_pay_cycle", UUIDType, ForeignKey("pay_cycle.id")),
    Column("fk_hours", UUIDType, ForeignKey("hours.id")),
)


class PayCycle(Base):
    __tablename__ = 'pay_cycle'

    id = Column(UUIDType(binary=False), primary_key=True)
    employee_id = Column(UUIDType(binary=False), ForeignKey('employee.id'))
    company_id = Column(UUIDType(binary=False), ForeignKey('company.id'))
    hours_logged = relationship(
        "Hours",
        backref="pay_cycle",
        secondary=paycycle_hours
    )
    start = Column(DateTime)
    end = Column(DateTime)

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'hours': [h.serialize for h in self.hours],
            'start': self.start,
            'end': self.end
        }


class Hours(Base):
    __tablename__ = 'hours'

    id = Column(UUIDType(binary=False), primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    total_hours = Column(Float)
    pay_cycles = relationship(
        "PayCycle",
        backref="hours",
        secondary=paycycle_hours
    )

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'total': self.total
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
