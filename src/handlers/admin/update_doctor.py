from ast import literal_eval
from typing import Dict, List, Any, Optional, Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup
import asyncio

from src.core.config import bot
from src.core.secrets import MASTER_ADMIN, PHOTO_GALLERY_PATH, PHOTO_EXTENSION
from src.core.enums import CallbackData, BotMessageText, Symbols, CacheKeys
from src.core.processing import transform_name, process_input
from src.core.validation import check_integer
from src.db import query
from src.db.models import Speciality
from src.handlers.admin.show_doctor import FSMShowDoctor
from src.keyboards import (
    science_degrees_list, doctor_info_sections, specialities_config,
    main_menu_client, qual_categories_list, show_specialities,
    change_info, show_doc_specialities, back_to_menu, show_doctors
)
from src.utils.cache import get_cache, update_cache
from src.utils.misc import logger

# this dict is used to understand what message text to send basing on update section (update doctor)
section_text: Dict[str, str] = {
    CallbackData.full_name.value: BotMessageText.ask_doctor_name.value,
    CallbackData.photo.value: BotMessageText.ask_doctor_photo.value,
    CallbackData.description.value: BotMessageText.ask_doctor_description.value,
    CallbackData.experience.value: BotMessageText.ask_doctor_experience.value,
    CallbackData.science_degree.value: BotMessageText.ask_doctor_science_degree.value,
    CallbackData.qual_category.value: BotMessageText.ask_doctor_qual_category.value,
}
# this dict is used to understand what reply_markup to send basing on update section (update doctor)
section_reply_markup: Dict[str, InlineKeyboardMarkup] = {
    CallbackData.full_name.value: back_to_menu(section=CallbackData.doctors_settings.value),
    CallbackData.photo.value: back_to_menu(section=CallbackData.doctors_settings.value),
    CallbackData.description.value: back_to_menu(section=CallbackData.doctors_settings.value),
    CallbackData.experience.value: back_to_menu(section=CallbackData.doctors_settings.value),
    CallbackData.science_degree.value: science_degrees_list,
    CallbackData.qual_category.value: qual_categories_list,
    CallbackData.price.value: back_to_menu(section=CallbackData.doctors_settings.value)
}


# define finite-state machine
class FSMUpdateDoctor(StatesGroup):
    doctor = State()
    section = State()
    speciality = State()
    cur_value = State()
    new_value = State()
    action = State()
    specialities_editing = State()
    price = State()


async def update_doctor(callback_query: types.CallbackQuery, state: FSMContext):
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
        await FSMUpdateDoctor.doctor.set()
        async with state.proxy() as data:
            # crate dictionaries to optimize callback_data
            data['doctors'], data['doctors_pool'] = {}, {}
            for uid, doctor in enumerate(doctors):
                data['doctors'][uid] = {}
                data['doctors'][uid]['name'] = doctor.full_name
                data['doctors'][uid]['photo'] = doctor.photo
                data['doctors_pool'][str(uid)] = doctor.full_name
            # save message id and user uid
            data['user_uid'] = callback_query.from_user.id
            data['last_msg_id'] = callback_query.message.message_id
            data['button_names'] = [transform_name(full_name=info['name']) for uid, info in data['doctors'].items()]
            # ask to choose doctor to update info
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_doctor.value,
                reply_markup=show_doctors(
                    doctors=data['doctors_pool'],
                    section=CallbackData.doctors_settings.value,
                    accept_btn=False
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


async def get_doctor(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    key: str
    doctor: Any
    bot_message: types.Message

    async with state.proxy() as data:
        # check if it is initial update session
        if 'chosen_doctor' in data:
            pass
        else:
            # get doctor key
            key = callback_query.data.split(Symbols.separator.value)[1]
            # get doctor info
            doctor = await query.get_doctor_by_photo(photo=data['doctors'][key]['photo'])
            # save obtained answer into FSM memory
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
        # check state
        if await state.get_state() == FSMShowDoctor.doctor.state:
            # delete message (because it's impossible to edit messages when you need to unpin photo)
            await bot.delete_message(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id']
            )
            # ask to choose section for editing
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_to_choose_section(doc_name=data['chosen_doctor'][CallbackData.full_name.value]),
                parse_mode='HTML',
                reply_markup=doctor_info_sections
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
        else:
            # ask to choose section for editing
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_section(doc_name=data['chosen_doctor'][CallbackData.full_name.value]),
                parse_mode='HTML',
                reply_markup=doctor_info_sections
            )
    # set bot to the section state
    await FSMUpdateDoctor.section.set()

    return


async def get_section(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    section: str

    # get section
    section = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['section'] = section
    # check chosen section
    if section == CallbackData.price.value:
        async with state.proxy() as data:
            # ask to choose speciality
            await callback_query.message.edit_text(
                text=BotMessageText.doc_specialities(
                    doc_name=data['chosen_doctor'][CallbackData.full_name.value]
                ),
                parse_mode='HTML',
                reply_markup=show_doc_specialities(
                    specialities=data['chosen_doctor'][CallbackData.speciality.value],
                    ids=data['chosen_doctor'][CallbackData.speciality_id.value]
                )
            )
        # set bot to the speciality state
        await FSMUpdateDoctor.speciality.set()
    else:
        async with state.proxy() as data:
            # show the current value and ask to choose next action
            await callback_query.message.edit_text(
                text=BotMessageText.current_value(
                    doc_name=data['chosen_doctor'][CallbackData.full_name.value],
                    value=data['chosen_doctor'][section],
                    section=data['section']
                ),
                parse_mode='HTML',
                reply_markup=change_info(section=CallbackData.choose_section.value)
            )
        # set bot to current value state
        await FSMUpdateDoctor.cur_value.set()

    return


async def get_speciality(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    speciality_id: int
    index: int

    # get speciality id
    speciality_id = int(callback_query.data.split(Symbols.separator.value)[1])
    async with state.proxy() as data:
        # find position in array
        index = data['chosen_doctor'][CallbackData.speciality_id.value].index(speciality_id)
        # save obtained result in the FSM memory
        data['index'] = index
        data['speciality'] = data['chosen_doctor'][CallbackData.speciality.value][index]
        data['speciality_id'] = speciality_id
        data['price'] = data['chosen_doctor'][CallbackData.price.value][index]
        # show the current value and ask to choose next action
        await callback_query.message.edit_text(
            text=BotMessageText.current_value(
                doc_name=data['chosen_doctor'][CallbackData.full_name.value],
                value=data['price'],
                section=data['section']
            ),
            parse_mode='HTML',
            reply_markup=change_info(
                section=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.price.value)
        )
    # set bot to the current value state
    await FSMUpdateDoctor.next()

    return


async def change_value(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        # check section
        if data['section'] == CallbackData.speciality.value:
            # ask to choose action (add/delete specialities)
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_action(doc_name=data['chosen_doctor'][CallbackData.full_name.value]),
                parse_mode='HTML',
                reply_markup=specialities_config
            )
            # set bot to the action state
            await FSMUpdateDoctor.action.set()
        else:
            # ask to enter new value
            await callback_query.message.edit_text(
                text=BotMessageText.ask_doctor_price(speciality=data['speciality']) \
                    if data['section'] == CallbackData.price.value else section_text[data['section']],
                parse_mode='HTML',
                reply_markup=section_reply_markup[data['section']]
            )
            # set bot to the new value state
            await FSMUpdateDoctor.next()

    return


"""
"get_new_value" function was separated into 3 functions with different input data types 
in order to make code more readable and exclude complicated if-else logic
"""


async def get_new_value_photo(message: types.Message, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]

    # get user uid
    user_uid = message.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # delete answer
    await message.delete()
    # check user access
    if user_uid == MASTER_ADMIN or user_uid in admins:
        async with state.proxy() as data:
            # check section
            if data['section'] != CallbackData.photo.value:
                pass
            else:
                if message.content_type == 'photo':
                    # ask to send photo in correct format
                    await bot.edit_message_text(
                        chat_id=user_uid,
                        message_id=data['last_msg_id'],
                        text=BotMessageText.ask_doctor_photo_again.value,
                        parse_mode='HTML',
                        reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
                    )
                else:
                    # save photo in the gallery
                    await message.document.download(
                        PHOTO_GALLERY_PATH + data['chosen_doctor'][CallbackData.photo.value] + PHOTO_EXTENSION)
                    # log photo update
                    logger.info(
                        f'admin {user_uid} changed "photo" of specialist '
                        f'"{data["chosen_doctor"][CallbackData.full_name.value]}"')
                    # send the "success message"
                    await bot.edit_message_text(
                        chat_id=user_uid,
                        message_id=data['last_msg_id'],
                        text=BotMessageText.successful_parameter_change.value
                    )
                    # set pause (give time to read)
                    await asyncio.sleep(2)
                    # ask to choose section for editing
                    await bot.edit_message_text(
                        chat_id=user_uid,
                        message_id=data['last_msg_id'],
                        text=BotMessageText.ask_to_choose_section(
                            doc_name=data['chosen_doctor'][CallbackData.full_name.value]
                        ),
                        parse_mode='HTML',
                        reply_markup=doctor_info_sections
                    )
                    # set bot to the section state
                    await FSMUpdateDoctor.section.set()
    else:
        async with state.proxy() as data:
            # send warning that user doesn't have enough privileges
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.lack_of_privileges.value
            )
            # set pause (give time to read)
            await asyncio.sleep(2)
            # move back to main menu
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.menu_desc(),
                parse_mode='HTML',
                reply_markup=main_menu_client
            )
        # exit FSM
        await state.finish()

    return


async def get_new_value_cb(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    callback_data: str
    new_value: Optional[str]

    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user access
    if user_uid == MASTER_ADMIN or user_uid in admins:
        # get admin choice
        callback_data = callback_query.data.split(Symbols.separator.value)[1]
        # identify choice
        new_value = None if callback_data == CallbackData.no_specification.value else callback_data
        async with state.proxy() as data:
            # update info
            await query.update_doctor(
                photo=data['chosen_doctor'][CallbackData.photo.value],
                column=data['section'],
                value=new_value
            )
            # log data update
            logger.info(
                f'admin {user_uid} changed "{data["section"]}" '
                f'of specialist "{data["chosen_doctor"][CallbackData.full_name.value]}" '
                f'from "{data["chosen_doctor"][data["section"]]}" to "{new_value}"'
            )
            # update value in the FSM memory
            data['chosen_doctor'][data['section']] = new_value
            # send the "success message"
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.successful_parameter_change.value
            )
            # set pause (give time to read)
            await asyncio.sleep(2)
            # ask to choose section for editing
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_to_choose_section(
                    doc_name=data['chosen_doctor'][CallbackData.full_name.value]
                ),
                parse_mode='HTML',
                reply_markup=doctor_info_sections
            )
        # set bot to the section state
        await FSMUpdateDoctor.section.set()
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


async def get_new_value_msg(message: types.Message, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    name: List[str]
    new_value: Union[int, str]
    speciality_id: Optional[int]
    log_speciality: str
    log_prev_value: Any
    msg_text: str
    msg_reply_markup: InlineKeyboardMarkup

    # get user uid
    user_uid = message.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user access
    if user_uid == MASTER_ADMIN or user_uid in admins:
        async with state.proxy() as data:
            # check section and process input
            if data['section'] == CallbackData.full_name.value:
                name = process_input(string=message.text, delimiter=' ')
                new_value = ' '.join(name)
            elif data['section'] == CallbackData.description.value:
                description = process_input(string=message.text, delimiter=',')
                new_value = ', '.join(description)
            elif data['section'] in [CallbackData.experience.value, CallbackData.price.value]:
                # validate input
                if not check_integer(message.text):
                    # delete answer
                    await message.delete()
                    # ask to enter value in integer format
                    await bot.edit_message_text(
                        chat_id=user_uid,
                        message_id=data['last_msg_id'],
                        text=BotMessageText.ask_doctor_experience_again.value \
                            if data['section'] == CallbackData.experience.value \
                            else BotMessageText.ask_doctor_price(speciality=data['speciality'],
                                                                 again=True),
                        parse_mode='HTML',
                        reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
                    )
                    # exit function
                    return
                else:
                    # process the input
                    new_value = int(message.text)
            else:
                # delete answer
                await message.delete()
                # exit function
                return
            # delete answer
            await message.delete()
            # set variables according to the section
            if data['section'] != CallbackData.price.value:
                speciality_id = None
                log_speciality = ""
                log_prev_value = data["chosen_doctor"][data["section"]]
                msg_text = BotMessageText.ask_to_choose_section(
                    doc_name=data['chosen_doctor'][CallbackData.full_name.value]
                    if data['section'] != CallbackData.full_name.value else new_value
                )
                msg_reply_markup = doctor_info_sections
            else:
                speciality_id = data['speciality_id']
                log_speciality = 'in speciality "' + data['speciality'] + '" '
                log_prev_value = data['price']
                msg_text = BotMessageText.doc_specialities(
                    doc_name=data['chosen_doctor'][CallbackData.full_name.value]
                )
                msg_reply_markup = show_doc_specialities(
                    specialities=data['chosen_doctor'][CallbackData.speciality.value],
                    ids=data['chosen_doctor'][CallbackData.speciality_id.value]
                )
            # update info
            await query.update_doctor(
                photo=data['chosen_doctor'][CallbackData.photo.value],
                column=data['section'],
                value=new_value,
                speciality_id=speciality_id
            )
            # log data update
            logger.info(
                f'admin {user_uid} changed "{data["section"]}" '
                f'of specialist "{data["chosen_doctor"][CallbackData.full_name.value]}" '
                f'{log_speciality}from "{log_prev_value}" to "{new_value}"'
            )
            # update value in the FSM memory and change state
            if data['section'] != CallbackData.price.value:
                data['chosen_doctor'][data['section']] = new_value
                # set bot to the section state
                await FSMUpdateDoctor.section.set()
            else:
                data['chosen_doctor'][data['section']][data['index']] = new_value
                # set bot to the speciality state
                await FSMUpdateDoctor.speciality.set()
            # send the "success message"
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.successful_parameter_change.value
            )
            # set pause (give time to read)
            await asyncio.sleep(2)
            # ask to choose section for editing
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=msg_text,
                parse_mode='HTML',
                reply_markup=msg_reply_markup
            )
    else:
        # delete answer
        await message.delete()
        # send warning that user doesn't have enough privileges
        async with state.proxy() as data:
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.lack_of_privileges.value
            )
            # set pause (give time to read)
            await asyncio.sleep(2)
            # move back to main menu
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
                text=BotMessageText.menu_desc(),
                parse_mode='HTML',
                reply_markup=main_menu_client
            )
        # exit FSM
        await state.finish()

    return


async def back_to_cur_value(callback_query: types.CallbackQuery, state: FSMContext):
    # set bot to the current value state
    await FSMUpdateDoctor.cur_value.set()
    async with state.proxy() as data:
        # show the current value and ask to choose next action
        await callback_query.message.edit_text(
            text=BotMessageText.current_value(
                doc_name=data['chosen_doctor'][CallbackData.full_name.value],
                value=data['chosen_doctor'][data['section']],
                section=data['section']
            ),
            parse_mode='HTML',
            reply_markup=change_info(section=CallbackData.choose_section.value)
        )

    return


async def get_action(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    specialities: List[str]

    async with state.proxy() as data:
        # check chosen action
        if callback_query.data == CallbackData.add_specialities.value:
            # get all the existing specialities
            specialities = await query.get_specialities()
            for item in data['chosen_doctor'][CallbackData.speciality.value]:
                specialities.remove(item)
            # create dictionary to optimize callback_data
            data['specialities_pool'] = dict(enumerate(specialities))
            data['specialities'], data['messages_to_del'] = [], []
            # save obtained answer into FSM memory
            data['action'] = CallbackData.add_specialities.value
            # ask to add/choose specialities
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_specify_specialities_to_add.value,
                parse_mode='HTML',
                reply_markup=show_specialities(
                    specialities=list(data['specialities_pool'].values()),
                    ids=list(data['specialities_pool'].keys()),
                    marked_specialities=[]
                )
            )
        else:
            # get all the doctor specialities
            specialities = await query.get_doctor_specialities(photo=data['chosen_doctor'][CallbackData.photo.value])
            # create dictionary to optimize callback_data
            data['specialities_pool'] = {speciality.id: speciality.title for speciality in specialities}
            data['specialities'] = []
            # save obtained answer into FSM memory
            data['action'] = CallbackData.delete_specialities.value
            # ask to add/choose specialities
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_specify_specialities_to_del.value,
                parse_mode='HTML',
                reply_markup=show_specialities(
                    specialities=list(data['specialities_pool'].values()),
                    ids=list(data['specialities_pool'].keys()),
                    marked_specialities=[],
                    delete=True
                )
            )
    # set bot to the specialities editing state
    await FSMUpdateDoctor.next()

    return


async def choose_specialities(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    speciality_id: str

    # get speciality id
    speciality_id = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # add/remove speciality choice
        # we use str type key as we have Redis storage which keeps data in string format
        if data['specialities_pool'][speciality_id] in data['specialities']:
            data['specialities'].remove(data['specialities_pool'][speciality_id])
        else:
            data['specialities'].append(data['specialities_pool'][speciality_id])
        # mark chosen speciality
        await callback_query.message.edit_reply_markup(
            reply_markup=show_specialities(
                specialities=list(data['specialities_pool'].values()),
                ids=list(data['specialities_pool'].keys()),
                marked_specialities=data['specialities'],
                delete=False if data['action'] == CallbackData.add_specialities.value else True
            )
        )

    return


async def create_new_specialities(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    bot_message: types.Message

    # ask to enter new specialities
    bot_message = await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=BotMessageText.ask_to_add_new_specialities.value,
        parse_mode='HTML'
    )
    # save message id
    async with state.proxy() as data:
        data['messages_to_del'].append(bot_message.message_id)

    return


async def get_new_specialities(message: types.Message, state: FSMContext):
    # annotation
    specialities: List[str]

    async with state.proxy() as data:
        if data['action'] == CallbackData.add_specialities.value:
            # process the input
            specialities = process_input(string=message.text, delimiter=',')
            # add specialities to FSM memory
            for speciality in specialities:
                if speciality not in data['specialities_pool'].values() \
                        and speciality not in data['chosen_doctor'][CallbackData.speciality.value]:
                    data['specialities'].append(speciality)
            # save messages id
            data['messages_to_del'].append(message.message_id)
        else:
            # delete message
            await message.delete()

    return


async def update_specialities(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    admins: List[int]
    cache_update_required: bool
    speciality_id: int
    index: int
    doctors: List[Any]

    async with state.proxy() as data:
        if data['action'] == CallbackData.add_specialities.value:
            # check if specialities are specified
            if len(data['specialities']) == 0:
                # exit function
                return
            # drop duplicates
            data['specialities'] = list(set(data['specialities']))
            # delete user answers (if needed)
            for msg_id in data['messages_to_del']:
                await bot.delete_message(
                    chat_id=data['user_uid'],
                    message_id=msg_id
                )
            data['messages_to_del'] = []
            # initialize prices array
            data['price'] = []
            # control entering prices
            data['no_price'] = data['specialities'].copy()
            # ask to enter price
            await callback_query.message.edit_text(
                text=BotMessageText.ask_doctor_price(speciality=data['no_price'][0]),
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
            )
            # set bot to the price state
            await FSMUpdateDoctor.next()
            # exit function
            return
        else:
            # check if all specialities are chosen
            if len(data['specialities']) == len(data['specialities_pool']):
                # inform that it's restricted to choose all specialities
                await callback_query.message.edit_text(
                    text=BotMessageText.warn_not_to_choose_all_specialities.value,
                    parse_mode='HTML',
                    reply_markup=show_specialities(
                        specialities=list(data['specialities_pool'].values()),
                        ids=list(data['specialities_pool'].keys()),
                        marked_specialities=data['specialities'],
                        delete=True
                    )
                )
                # exit function
                return
            else:
                # get admins
                admins = await get_cache(key=CacheKeys.admins.value)
                # check user access
                if data['user_uid'] == MASTER_ADMIN or data['user_uid'] in admins:
                    # set the flag to understand if it is needed to update cache
                    cache_update_required = False
                    for speciality in data['specialities']:
                        # get speciality id
                        speciality_id = list(data['specialities_pool'].keys())[
                            list(data['specialities_pool'].values()).index(speciality)]
                        # delete doctor with specified speciality
                        await query.delete_doctor(
                            photo=data['chosen_doctor'][CallbackData.photo.value],
                            speciality_id=int(speciality_id)
                        )
                        # update values in the FSM memory
                        index = data['chosen_doctor'][data['section']].index(speciality)
                        data['chosen_doctor'][data['section']].remove(speciality)
                        data['chosen_doctor'][CallbackData.speciality_id.value].remove(int(speciality_id))
                        del data['chosen_doctor'][CallbackData.price.value][index]
                        # get all the doctors for the speciality
                        doctors = await query.get_doctors_by_speciality(id=int(speciality_id))
                        # check if there are any doctors left
                        if len(doctors) == 0:
                            # delete speciality if there is no doctors left
                            await query.delete_speciality(speciality_id=int(speciality_id))
                            # log the speciality deletion
                            logger.info(f'admin {data["user_uid"]} deleted speciality "{speciality}"')
                            # change flag
                            cache_update_required = True
                    # log the specialities deletion
                    logger.info(f'admin {data["user_uid"]} deleted specialities "{", ".join(data["specialities"])}" '
                                f'from doctor "{data["chosen_doctor"][CallbackData.full_name.value]}"')
                    # delete used keys
                    del data['specialities'], data['specialities_pool']
                    # send the "success message"
                    await callback_query.message.edit_text(text=BotMessageText.successful_parameter_change.value)
                    # set pause (give time to read)
                    await asyncio.sleep(2)
                    # check if it is needed to update cache
                    if cache_update_required:
                        # update specialities in cache
                        await update_cache(CacheKeys.specialities.value)
                    # ask to choose action (add/delete specialities)
                    await bot.edit_message_text(
                        chat_id=data['user_uid'],
                        message_id=data['last_msg_id'],
                        text=BotMessageText.ask_to_choose_action(
                            doc_name=data['chosen_doctor'][CallbackData.full_name.value]),
                        parse_mode='HTML',
                        reply_markup=specialities_config
                    )
                    # set bot to the action state
                    await FSMUpdateDoctor.action.set()
                    # exit function
                    return
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


async def get_price(message: types.Message, state: FSMContext):
    # annotation
    admins: List[int]
    cache_update_required: bool
    res: Speciality

    # validate input
    if not check_integer(message.text):
        # delete answer
        await message.delete()
        async with state.proxy() as data:
            # ask to provide price in integer format
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_doctor_price(
                    speciality=data['no_price'][0],
                    again=True
                ),
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
            )
        # exit function
        return
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['price'].append(int(message.text))
            # delete speciality with obtained price
            del data['no_price'][0]
            # delete answer
            await message.delete()
            # check if there are any specialities left
            if len(data['no_price']) != 0:
                # ask to enter price for the next speciality
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.ask_doctor_price(speciality=data['no_price'][0]),
                    parse_mode='HTML',
                    reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
                )
                # exit function
                return
            else:
                # get admins
                admins = await get_cache(key=CacheKeys.admins.value)
                # check user access
                if data['user_uid'] == MASTER_ADMIN or data['user_uid'] in admins:
                    # delete used key
                    del data['no_price']
                    # create empty array to store specialities id
                    data['speciality_id'] = []
                    # set the flag to understand if it is needed to update cache
                    cache_update_required = False
                    for speciality in data['specialities']:
                        # check if speciality is new
                        if speciality not in data['specialities_pool'].values():
                            # create speciality
                            res = await query.create_speciality(title=speciality)
                            # save speciality id
                            data['speciality_id'].append(res.id)
                            # log the speciality creation
                            logger.info(f'admin {data["user_uid"]} created speciality "{speciality}"')
                            # change flag
                            cache_update_required = True
                        else:
                            # get speciality to obtain id
                            res = await query.get_speciality_by_title(title=speciality)
                            # save speciality id
                            data['speciality_id'].append(res.id)
                        # add doctor to the db
                        await query.create_doctor(
                            full_name=data['chosen_doctor'][CallbackData.full_name.value],
                            photo=data['chosen_doctor'][CallbackData.photo.value],
                            description=data['chosen_doctor'][CallbackData.description.value],
                            speciality_title=speciality,
                            experience=data['chosen_doctor'][CallbackData.experience.value],
                            science_degree=data['chosen_doctor'][CallbackData.science_degree.value],
                            qual_category=data['chosen_doctor'][CallbackData.qual_category.value],
                            price=data['price'][data['specialities'].index(speciality)]
                        )
                    # log the speciality addition
                    logger.info(
                        f'admin {data["user_uid"]} added specialities "{", ".join(data["specialities"])}" '
                        f'to doctor "{data["chosen_doctor"][CallbackData.full_name.value]}"')
                    # update values in the FSM memory
                    data['chosen_doctor'][data['section']] += data['specialities']
                    data['chosen_doctor'][CallbackData.price.value] += data['price']
                    data['chosen_doctor'][CallbackData.speciality_id.value] += data['speciality_id']
                    # delete used keys
                    del data['specialities'], data['specialities_pool'], data['speciality_id']
                    # send the "success message"
                    await bot.edit_message_text(
                        chat_id=data['user_uid'],
                        message_id=data['last_msg_id'],
                        text=BotMessageText.successful_parameter_change.value
                    )
                    # set pause (give time to read)
                    await asyncio.sleep(2)
                    # check if it is needed to update cache
                    if cache_update_required:
                        # update specialities in cache
                        await update_cache(CacheKeys.specialities.value)
                    # ask to choose action (add/delete specialities)
                    await bot.edit_message_text(
                        chat_id=data['user_uid'],
                        message_id=data['last_msg_id'],
                        text=BotMessageText.ask_to_choose_action(
                            doc_name=data['chosen_doctor'][CallbackData.full_name.value]),
                        parse_mode='HTML',
                        reply_markup=specialities_config
                    )
                    # set bot to the action state
                    await FSMUpdateDoctor.action.set()
                    # exit function
                    return
                else:
                    # send warning that user doesn't have enough privileges
                    await bot.edit_message_text(
                        chat_id=data['user_uid'],
                        message_id=data['last_msg_id'],
                        text=BotMessageText.lack_of_privileges.value
                    )
                    # set pause (give time to read)
                    await asyncio.sleep(2)
                    # move back to main menu
                    await bot.edit_message_text(
                        chat_id=data['user_uid'],
                        message_id=data['last_msg_id'],
                        text=BotMessageText.menu_desc(),
                        parse_mode='HTML',
                        reply_markup=main_menu_client
                    )
        # exit FSM
        await state.finish()

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        update_doctor,
        lambda x: x.data and x.data == CallbackData.update_doctor.value,
        state='*'
    )
    dp.register_callback_query_handler(
        get_doctor,
        lambda x: x.data and x.data.startswith(CallbackData.choose_person.value),
        state=FSMUpdateDoctor.doctor
    )
    dp.register_callback_query_handler(
        get_doctor,
        lambda x: x.data and x.data in [CallbackData.choose_section.value, CallbackData.edit.value],
        state=[FSMUpdateDoctor.speciality, FSMUpdateDoctor.cur_value, FSMShowDoctor.doctor]
    )
    dp.register_callback_query_handler(
        get_section,
        lambda x: x.data and x.data.startswith(CallbackData.choose_section.value),
        state=[FSMUpdateDoctor.section, FSMUpdateDoctor.cur_value]
    )
    dp.register_callback_query_handler(
        get_speciality,
        lambda x: x.data and x.data.startswith(CallbackData.speciality_title.value + Symbols.separator.value),
        state=FSMUpdateDoctor.speciality
    )
    dp.register_callback_query_handler(
        change_value,
        lambda x: x.data and x.data == CallbackData.change_info.value,
        state=FSMUpdateDoctor.cur_value
    )
    dp.register_message_handler(
        get_new_value_photo,
        state=FSMUpdateDoctor.new_value,
        content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT]
    )
    dp.register_callback_query_handler(
        get_new_value_cb,
        lambda x: x.data and (
                x.data.startswith(CallbackData.choose_science_degree.value)
                or x.data.startswith(CallbackData.choose_qual_category.value)
        ),
        state=FSMUpdateDoctor.new_value,
    )
    dp.register_message_handler(
        get_new_value_msg,
        state=FSMUpdateDoctor.new_value,
        content_types=types.ContentType.TEXT
    )
    dp.register_callback_query_handler(
        get_action,
        lambda x: x.data and x.data in [CallbackData.add_specialities.value, CallbackData.delete_specialities.value],
        state=FSMUpdateDoctor.action
    )
    dp.register_callback_query_handler(
        choose_specialities,
        lambda x: x.data and x.data.startswith(CallbackData.speciality_title.value),
        state=FSMUpdateDoctor.specialities_editing
    )
    dp.register_callback_query_handler(
        create_new_specialities,
        lambda x: x.data and x.data == CallbackData.new_specialities.value,
        state=FSMUpdateDoctor.specialities_editing
    )
    dp.register_message_handler(
        get_new_specialities,
        state=FSMUpdateDoctor.specialities_editing
    )
    dp.register_callback_query_handler(
        update_specialities,
        lambda x: x.data and x.data == CallbackData.selection_completed.value,
        state=FSMUpdateDoctor.specialities_editing
    )
    dp.register_message_handler(
        get_price,
        state=FSMUpdateDoctor.price
    )
    dp.register_callback_query_handler(
        back_to_cur_value,
        lambda x: x.data and x.data == CallbackData.cur_value.value,
        state=FSMUpdateDoctor.action
    )

    return
