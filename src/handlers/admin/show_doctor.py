from ast import literal_eval
from typing import List, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.core.config import bot
from src.core.enums import CallbackData, BotMessageText, Symbols, CacheKeys
from src.core.secrets import MASTER_ADMIN, PHOTO_GALLERY_PATH, PHOTO_EXTENSION
from src.db import query
from src.keyboards import show_doctors, doctor_card, back_to_menu
from src.utils.cache import get_cache


# define finite-state machine
class FSMShowDoctor(StatesGroup):
    doctor = State()


async def show_doctor(callback_query: types.CallbackQuery, state: FSMContext):
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
        await FSMShowDoctor.doctor.set()
        async with state.proxy() as data:
            # crate dictionaries to optimize callback_data
            data['doctors'], data['doctors_pool'] = {}, {}
            for uid, doctor in enumerate(doctors):
                data['doctors'][uid] = {}
                data['doctors'][uid]['name'] = doctor.full_name
                data['doctors'][uid]['photo'] = doctor.photo
                data['doctors_pool'][str(uid)] = doctor.full_name
            # ask to choose doctor
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_card.value,
                reply_markup=show_doctors(
                    doctors=data['doctors_pool'],
                    section=CallbackData.doctors_settings.value,
                    accept_btn=False
                )
            )
            # save message id and user uid
            data['user_uid'] = callback_query.from_user.id
            data['last_msg_id'] = callback_query.message.message_id
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )

    return


async def get_doctor(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    key: str
    doctor: Any
    bot_message: types.Message

    # get doctor key
    key = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # get doctor info
        doctor = await query.get_doctor_by_photo(photo=data['doctors'][key]['photo'])
        data['chosen_doctor'] = {}
        data['chosen_doctor'][CallbackData.full_name.value] = doctor.full_name
        data['chosen_doctor'][CallbackData.photo.value] = doctor.photo
        data['chosen_doctor'][CallbackData.description.value] = doctor.description
        data['chosen_doctor'][CallbackData.speciality_id.value] = literal_eval(doctor.speciality_id)
        data['chosen_doctor'][CallbackData.speciality.value] = literal_eval(doctor.speciality)
        data['chosen_doctor'][CallbackData.experience.value] = doctor.experience
        data['chosen_doctor'][CallbackData.science_degree.value] = doctor.science_degree
        data['chosen_doctor'][CallbackData.qual_category.value] = doctor.qual_category
        data['chosen_doctor'][CallbackData.price.value] = literal_eval(doctor.price)
        # delete message (because it's impossible to edit messages when you need to attach photo)
        await bot.delete_message(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id']
        )
        # send doctor's card
        path = PHOTO_GALLERY_PATH + doctor.photo + PHOTO_EXTENSION
        with open(path, 'rb') as photo:
            bot_message = await bot.send_photo(
                chat_id=data['user_uid'],
                photo=photo,
                caption=BotMessageText.doctor_info(
                    full_name=data['chosen_doctor'][CallbackData.full_name.value],
                    description=data['chosen_doctor'][CallbackData.description.value],
                    experience=data['chosen_doctor'][CallbackData.experience.value],
                    science_degree=data['chosen_doctor'][CallbackData.science_degree.value],
                    qual_category=data['chosen_doctor'][CallbackData.qual_category.value],
                    price=data['chosen_doctor'][CallbackData.price.value],
                    speciality=data['chosen_doctor'][CallbackData.speciality.value]
                ),
                parse_mode='HTML',
                reply_markup=doctor_card
            )
        # update message id
        data['last_msg_id'] = bot_message.message_id

    return


async def move_back_to_doctors(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    bot_message: types.Message

    async with state.proxy() as data:
        # delete message (because it's impossible to edit messages when you need to unpin photo)
        await bot.delete_message(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id']
        )
        # send doctors list
        bot_message = await bot.send_message(
            chat_id=data['user_uid'],
            text=BotMessageText.ask_to_choose_card.value,
            reply_markup=show_doctors(
                doctors=data['doctors_pool'],
                section=CallbackData.doctors_settings.value,
                accept_btn=False
            )
        )
        # update message id
        data['last_msg_id'] = bot_message.message_id

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        show_doctor,
        lambda x: x.data and x.data == CallbackData.show_doctor.value,
        state='*'
    )
    dp.register_callback_query_handler(
        get_doctor,
        lambda x: x.data and x.data.startswith(CallbackData.choose_person.value),
        state=FSMShowDoctor.doctor
    )
    dp.register_callback_query_handler(
        move_back_to_doctors,
        lambda x: x.data and x.data == CallbackData.back_to_doctors.value,
        state=FSMShowDoctor.doctor
    )

    return
