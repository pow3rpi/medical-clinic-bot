from typing import Any, List
import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

from src.core.enums import CallbackData, BotMessageText, Symbols, CacheKeys
from src.core.secrets import MASTER_ADMIN, PHOTO_GALLERY_PATH, PHOTO_EXTENSION
from src.db import query
from src.keyboards import (
    doctors_settings_menu, confirmation_menu,
    show_doctors, back_to_menu, main_menu_client,
)
from src.utils.cache import get_cache, update_cache
from src.utils.misc import logger


# define finite-state machine
class FSMDeleteDoctor(StatesGroup):
    doctors = State()
    confirmation = State()


async def delete_doctor(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    doctors: List[Any]

    # exit FSM (if not finished)
    await state.finish()
    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user status (admin or not)
    if user_uid == MASTER_ADMIN or user_uid in admins:
        # get all the existing doctors
        doctors = await query.get_doctors()
        # set the first state (enter FSM)
        await FSMDeleteDoctor.doctors.set()
        async with state.proxy() as data:
            # save message id and user uid
            data['last_msg_id'] = callback_query.message.message_id
            data['user_uid'] = user_uid
            # crate dictionaries to optimize callback_data
            data['doctors'], data['doctors_pool'], data['chosen_doctors'] = {}, {}, {}
            for uid, doctor in enumerate(doctors):
                data['doctors'][str(uid)] = {}
                data['doctors'][str(uid)]['name'] = doctor.full_name
                data['doctors'][str(uid)]['photo'] = doctor.photo
                data['doctors_pool'][str(uid)] = doctor.full_name
            # ask to choose doctors for deletion
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_doctors.value,
                parse_mode='HTML',
                reply_markup=show_doctors(
                    doctors=data['doctors_pool'],
                    section=CallbackData.doctors_settings.value,
                    marked_uids=[]
                )
            )
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )

    return


async def choose_doctors(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    key: str

    # get doctor key
    key = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # add/remove doctor choice
        # we use str type key as we have Redis storage which keeps data in string format
        if key in data['chosen_doctors'].keys():
            del data['chosen_doctors'][key]
        else:
            data['chosen_doctors'][key] = {}
            data['chosen_doctors'][key]['name'] = data['doctors'][key]['name']
            data['chosen_doctors'][key]['photo'] = data['doctors'][key]['photo']
        # mark chosen doctor
        await callback_query.message.edit_reply_markup(
            reply_markup=show_doctors(
                doctors=data['doctors_pool'],
                section=CallbackData.doctors_settings.value,
                marked_uids=list(data['chosen_doctors'].keys())
            )
        )

    return


async def get_doctors(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        # ask to confirm the deletion
        await callback_query.message.edit_text(
            text=BotMessageText.confirm_deletion([doc['name'] for doc in data['chosen_doctors'].values()]),
            parse_mode='HTML',
            reply_markup=confirmation_menu(section=CallbackData.doctors_settings.value)
        )
    # set bot to the confirmation state
    await FSMDeleteDoctor.next()

    return


async def get_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    cache_update_required: bool
    specialities: List[Any]
    doctors: List[Any]
    specialities_array: List[str]

    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user status (admin or not)
    if user_uid == MASTER_ADMIN or user_uid in admins:
        # set the flag to understand if it is needed to update cache
        cache_update_required = False
        async with state.proxy() as data:
            for uid, info in data['chosen_doctors'].items():
                # get specialities that doctor has
                specialities = await query.get_doctor_specialities(photo=info['photo'])
                # delete doctor
                await query.delete_doctor(photo=info['photo'])
                specialities_array = []
                for speciality in specialities:
                    specialities_array.append(speciality.title)
                # log the doctor deletion
                logger.info(f'admin {user_uid} deleted doctor "{info["name"]}" '
                            f'with specialities "{", ".join(specialities_array)}"')
                # delete photo from the gallery
                os.remove(PHOTO_GALLERY_PATH + info['photo'] + PHOTO_EXTENSION)
                for speciality in specialities:
                    # get all the doctors for the speciality
                    doctors = await query.get_doctors_by_speciality(id=speciality.id)
                    # check if there are any doctors left
                    if len(doctors) == 0:
                        # delete speciality if there is no doctors left
                        await query.delete_speciality(speciality_id=speciality.id)
                        # log the speciality deletion
                        logger.info(f'admin {user_uid} deleted speciality "{speciality.title}"')
                        # change flag
                        cache_update_required = True
        # send the "success message"
        await callback_query.message.edit_text(text=BotMessageText.successful_doctors_deletion.value)
        # set pause (give time to read)
        await asyncio.sleep(2)
        # check if it is needed to update cache
        if cache_update_required:
            # update specialities in cache
            await update_cache(CacheKeys.specialities.value)
        # move back to menu
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=doctors_settings_menu
        )
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(text=BotMessageText.lack_of_privileges.value)
        # set pause (give time to read)
        await asyncio.sleep(2)
        # move back to main menu
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=main_menu_client
        )
    # exit FSM
    await state.finish()

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        delete_doctor,
        lambda x: x.data and x.data == CallbackData.delete_doctor.value,
        state='*'
    )
    dp.register_callback_query_handler(
        choose_doctors,
        lambda x: x.data and x.data.startswith(CallbackData.choose_person.value),
        state=FSMDeleteDoctor.doctors
    )
    dp.register_callback_query_handler(
        get_doctors,
        lambda x: x.data and x.data == CallbackData.selection_completed.value,
        state=FSMDeleteDoctor.doctors
    )
    dp.register_callback_query_handler(
        delete_doctor,
        lambda x: x.data and x.data == CallbackData.change_choice.value,
        state=FSMDeleteDoctor.confirmation
    )
    dp.register_callback_query_handler(
        get_confirmation,
        lambda x: x.data and x.data == CallbackData.confirmation.value,
        state=FSMDeleteDoctor.confirmation
    )

    return
