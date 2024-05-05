from sqlalchemy import (
    Column, Integer, BigInteger, UniqueConstraint,
    Text, Enum, ForeignKey, DateTime, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.enums import (
    AdminPrivilegeType, ConsultationType,
    CommunicationType, ScienceDegree, QualCategory
)
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_uid = Column(BigInteger, unique=True, nullable=False)
    dt = Column(DateTime, nullable=False, server_default=func.now())

    profile = relationship('UserProfile', back_populates='user')
    appointment = relationship('Appointment', back_populates='user')
    callback = relationship('CallBack', back_populates='user')
    feedback = relationship('Feedback', back_populates='user')


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(Integer, ForeignKey('users.id'))
    username = Column(String(length=32))
    full_name = Column(String(length=64))
    phone = Column(String(length=11))

    user = relationship('User', back_populates='profile')

    __table_args__ = (
        UniqueConstraint(
            'username', 'full_name', 'phone',
            name='user_profile_constraint'
        ),
    )


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(Integer, ForeignKey('users.id'))
    consultation_type = Column(Enum(ConsultationType))
    communication_type = Column(Enum(CommunicationType))
    user_request = Column(Text, nullable=False)
    doctor_id = Column(Integer)
    preferable_dt = Column(Text)
    dt = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship('User', back_populates='appointment')


class CallBack(Base):
    __tablename__ = 'callbacks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(Integer, ForeignKey('users.id'))
    dt = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship('User', back_populates='callback')


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    dt = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship('User', back_populates='feedback')


class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(length=64), nullable=False)
    photo = Column(String(length=32), nullable=False)
    description = Column(Text, nullable=False)
    speciality_id = Column(Integer, ForeignKey('specialities.id'))
    experience = Column(Integer)
    science_degree = Column(Enum(ScienceDegree))
    qual_category = Column(Enum(QualCategory))
    price = Column(Integer, nullable=False)
    dt = Column(DateTime, nullable=False, server_default=func.now())

    speciality = relationship('Speciality', back_populates='doctor', lazy='joined')


class Speciality(Base):
    __tablename__ = 'specialities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=32), nullable=False)

    doctor = relationship('Doctor', back_populates='speciality')


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(BigInteger, nullable=False)
    full_name = Column(String(length=64), nullable=False)
    privilege_type = Column(Enum(AdminPrivilegeType))
    dt = Column(DateTime, nullable=False, server_default=func.now())
