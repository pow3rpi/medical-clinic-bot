from datetime import datetime
from typing import Any, List, Optional

import sqlalchemy as sa

from .base import Base
from .models import (
    UserProfile, Appointment, User, Admin,
    Feedback, Doctor, Speciality, CallBack
)
from .session import get_async_session


async def get_or_create_user(session, tg_uid: int, username: Optional[str],
                             full_name: Optional[str] = None, phone: Optional[str] = None) -> User:
    query = sa.select(User) \
        .filter(User.tg_uid == tg_uid)
    user = await session.execute(query)
    user = user.scalars().first()
    if not user:
        user = User(tg_uid=tg_uid)
        profile = UserProfile(
            user=user,
            username=username,
            full_name=full_name,
            phone=phone
        )
        session.add_all([user, profile])
        await session.commit()
    else:
        if not full_name:
            if not username:
                return user
            query = sa.select(UserProfile).filter(
                UserProfile.user_uid == user.id,
                UserProfile.username == username
            )
        else:
            if not phone:
                query = sa.select(UserProfile).filter(
                    UserProfile.user_uid == user.id,
                    UserProfile.username == username,
                    UserProfile.full_name == full_name
                )
            else:
                query = sa.select(UserProfile).filter(
                    UserProfile.user_uid == user.id,
                    UserProfile.username == username,
                    UserProfile.phone == phone,
                    UserProfile.full_name == full_name
                )
        profile = await session.execute(query)
        profile = profile.scalars().first()
        if not profile:
            profile = UserProfile(
                user=user,
                username=username,
                full_name=full_name,
                phone=phone
            )
            session.add(profile)
            await session.commit()

    return user


async def create_appointment(tg_uid: int, username: Optional[str], full_name: str, phone: Optional[str],
                             consultation_type: str, communication_type: str, user_request: str,
                             doctor_id: int, preferable_dt: Optional[str]) -> Appointment:
    async with get_async_session() as session:
        user = await get_or_create_user(
            session=session,
            tg_uid=tg_uid,
            username=username,
            full_name=full_name,
            phone=phone
        )
        appointment = Appointment(
            user=user,
            consultation_type=consultation_type,
            communication_type=communication_type,
            user_request=user_request,
            doctor_id=doctor_id,
            preferable_dt=preferable_dt
        )
        session.add(appointment)
        await session.commit()

        return appointment


async def create_callback(tg_uid: int, username: Optional[str], full_name: str, phone: str) -> CallBack:
    async with get_async_session() as session:
        user = await get_or_create_user(
            session=session,
            tg_uid=tg_uid,
            username=username,
            full_name=full_name,
            phone=phone
        )
        callback = CallBack(user=user)
        session.add(callback)
        await session.commit()

        return callback


async def create_feedback(tg_uid: int, username: Optional[str], message: str) -> Feedback:
    async with get_async_session() as session:
        user = await get_or_create_user(
            session=session,
            tg_uid=tg_uid,
            username=username
        )
        feedback = Feedback(
            user=user,
            message=message
        )
        session.add(feedback)
        await session.commit()

        return feedback


async def get_specialities() -> List[str]:
    async with get_async_session() as session:
        query = sa.select(Speciality.title) \
            .order_by(Speciality.title.asc())
        specialities = await session.execute(query)
        specialities = specialities.scalars().all()

        return specialities


async def get_speciality_by_title(title: str) -> Speciality:
    async with get_async_session() as session:
        query = sa.select(Speciality) \
            .filter(Speciality.title == title)
        speciality = await session.execute(query)
        speciality = speciality.scalars().first()

        return speciality


async def create_speciality(title: str) -> Speciality:
    async with get_async_session() as session:
        speciality = Speciality(title=title)
        session.add(speciality)
        await session.commit()

        return speciality


async def delete_speciality(speciality_id: int) -> None:
    async with get_async_session() as session:
        query = sa.delete(Speciality) \
            .filter(Speciality.id == speciality_id)
        await session.execute(query)
        await session.commit()

        return


async def get_doctors() -> List[Any]:
    async with get_async_session() as session:
        query = sa.select(Doctor.photo.distinct().label('photo'), Doctor.full_name) \
            .order_by(Doctor.full_name.asc())
        doctors = await session.execute(query)
        doctors = doctors.all()

        return doctors


async def get_doctors_by_speciality(**attribute) -> List[Any]:
    async with get_async_session() as session:
        query = sa.select(Doctor) \
            .filter(Doctor.speciality.has(**attribute)) \
            .order_by(Doctor.price.desc())
        doctors = await session.execute(query)
        doctors = doctors.scalars().all()

        return doctors


async def get_doctor_specialities(photo: str) -> List[Any]:
    async with get_async_session() as session:
        query = sa.select(Doctor.speciality_id.label('id'), Speciality.title.label('title')) \
            .join_from(Doctor, Speciality) \
            .filter(Doctor.photo == photo)
        specialities = await session.execute(query)
        specialities = specialities.all()

        return specialities


async def get_doctor_by_photo(photo: str) -> Any:
    async with get_async_session() as session:
        query = sa.select(
            Doctor.full_name, Doctor.photo, Doctor.description,
            sa.func.json_arrayagg(Doctor.speciality_id).label('speciality_id'),
            sa.func.json_arrayagg(Speciality.title).label('speciality'),
            Doctor.experience, Doctor.science_degree, Doctor.qual_category,
            sa.func.json_arrayagg(Doctor.price).label('price')
        ) \
            .join_from(Doctor, Speciality) \
            .group_by(Doctor.full_name, Doctor.photo, Doctor.description,
                      Doctor.experience, Doctor.science_degree, Doctor.qual_category) \
            .filter(Doctor.photo == photo)
        doctor = await session.execute(query)
        doctor = doctor.first()

        return doctor


async def create_doctor(full_name: str, photo: str, description: str, speciality_title: str,
                        experience: int, science_degree: str, qual_category: str, price: int) -> Doctor:
    async with get_async_session() as session:
        speciality = await get_speciality_by_title(speciality_title)
        doctor = Doctor(
            full_name=full_name,
            photo=photo,
            description=description,
            speciality=speciality,
            experience=experience,
            science_degree=science_degree,
            qual_category=qual_category,
            price=price
        )
        session.add(doctor)
        await session.commit()

        return doctor


async def update_doctor(photo: str, column: str, value: Any, speciality_id: int = None) -> None:
    async with get_async_session() as session:
        if not speciality_id:
            query = sa.update(Doctor) \
                .filter(Doctor.photo == photo) \
                .values({column: value})
        else:
            query = sa.update(Doctor) \
                .filter(Doctor.photo == photo,
                        Doctor.speciality_id == speciality_id) \
                .values({column: value})
        await session.execute(query)
        await session.commit()

        return


async def delete_doctor(photo: str, speciality_id: int = None) -> None:
    async with get_async_session() as session:
        if not speciality_id:
            query = sa.delete(Doctor) \
                .filter(Doctor.photo == photo)
        else:
            query = sa.delete(Doctor) \
                .filter(Doctor.photo == photo,
                        Doctor.speciality_id == speciality_id)
        await session.execute(query)
        await session.commit()

        return


async def get_price(photo: str, speciality: str) -> int:
    async with get_async_session() as session:
        query = sa.select(Doctor.price) \
            .filter(Doctor.photo == photo,
                    Doctor.speciality.has(title=speciality))
        price = await session.execute(query)
        price = price.scalars().first()

        return price


async def calculate_statistic(table: Base, start_date: datetime, end_date: datetime,
                              consultation_type: str = None) -> int:
    async with get_async_session() as session:
        if table == Appointment:
            query = sa.select(sa.func.count(table.dt)).filter(
                table.dt >= start_date,
                table.dt < end_date,
                table.consultation_type == consultation_type
            )
        else:
            query = sa.select(sa.func.count(table.dt)).filter(
                table.dt >= start_date,
                table.dt < end_date
            )
        n = await session.execute(query)
        n = n.scalar()

        return n


async def get_admins_ids(privilege_type: str = None) -> List[int]:
    async with get_async_session() as session:
        if not privilege_type:
            query = sa.select(Admin.user_uid)
        else:
            query = sa.select(Admin.user_uid) \
                .filter(Admin.privilege_type == privilege_type)
        admins = await session.execute(query)
        admins = admins.scalars().all()

        return admins


async def get_admins(privilege_type: str = None) -> List[Any]:
    async with get_async_session() as session:
        if not privilege_type:
            query = sa.select(Admin.user_uid, Admin.full_name)
        else:
            query = sa.select(Admin.user_uid, Admin.full_name) \
                .filter(Admin.privilege_type == privilege_type)
        admins = await session.execute(query)
        admins = admins.all()

        return admins


async def create_admin(user_uid: int, full_name: str, privilege_type: str) -> Admin:
    async with get_async_session() as session:
        admin = Admin(
            user_uid=user_uid,
            full_name=full_name,
            privilege_type=privilege_type
        )
        session.add(admin)
        await session.commit()

        return admin


async def delete_admin(user_uid: int) -> None:
    async with get_async_session() as session:
        query = sa.delete(Admin) \
            .filter(Admin.user_uid == user_uid)
        await session.execute(query)
        await session.commit()

        return
