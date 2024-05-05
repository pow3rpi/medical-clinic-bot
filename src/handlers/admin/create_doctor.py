from os import listdir
from typing import List, Optional
import uuid

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

from src.core.config import bot
from src.core.enums import CallbackData, BotMessageText, Symbols, CacheKeys
from src.core.processing import process_input
from src.core.secrets import MASTER_ADMIN, PHOTO_GALLERY_PATH, PHOTO_EXTENSION
from src.core.validation import check_integer
from src.db import query
from src.keyboards import (
    show_specialities, qual_categories_list, main_menu_client,
    confirmation_menu, science_degrees_list, back_to_menu,
    doctors_settings_menu, experience_specification
)
from src.utils.cache import get_cache, update_cache
from src.utils.misc import logger


# define finite-state machine
class FSMCreateDoctor(StatesGroup):
    speciality = State()
    name = State()
    photo = State()
    description = State()
    experience_choice = State()
    experience = State()
    science_degree = State()
    qual_category = State()
    price = State()
    confirmation = State()


async def create_doctor(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    specialities: List[str]

    # exit FSM (if not finished)
    await state.finish()
    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user status (admin or not)
    if user_uid == MASTER_ADMIN or user_uid in admins:
        # get all the existing specialities
        specialities = await query.get_specialities()
        # set the first state (enter FSM)
        await FSMCreateDoctor.speciality.set()
        async with state.proxy() as data:
            # save message id and user uid
            data['last_msg_id'] = callback_query.message.message_id
            data['user_uid'] = callback_query.from_user.id
            # crate dictionary to optimize callback_data
            data['specialities_pool'] = dict(enumerate(specialities))
            data['specialities'], data['messages_to_del'] = [], []
            # ask to choose specialities
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_specialities.value,
                parse_mode='HTML',
                reply_markup=show_specialities(
                    specialities=list(data['specialities_pool'].values()),
                    ids=list(data['specialities_pool'].keys()),
                    marked_specialities=[]
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


async def choose_specialities(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    speciality_id: str

    # get chosen speciality id
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
                marked_specialities=data['specialities']
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

    # process the input
    specialities = process_input(string=message.text, delimiter=',')
    # add specialities to FSM memory
    async with state.proxy() as data:
        for speciality in specialities:
            if speciality not in data['specialities_pool'].values():
                data['specialities'].append(speciality)
        # save messages id
        data['messages_to_del'].append(message.message_id)

    return


async def get_specialities(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
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
        # ask to enter name
        await callback_query.message.edit_text(
            text=BotMessageText.ask_doctor_name.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )
    # set bot to the name state
    await FSMCreateDoctor.next()

    return


async def get_name(message: types.Message, state: FSMContext):
    # annotation
    name: List[str]

    # process the input
    name = process_input(string=message.text, delimiter=' ')
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['name'] = ' '.join(name)
        # delete answer
        await message.delete()
        # ask to provide photo
        await bot.edit_message_text(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            text=BotMessageText.ask_doctor_photo.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )
    # set bot to the photo state
    await FSMCreateDoctor.next()

    return


async def get_photo(message: types.Message, state: FSMContext):
    # annotation
    all_files: List[str]
    file_name: str

    # check input type
    if message.content_type != 'document':
        # delete answer
        await message.delete()
        # ask to send photo in correct format
        async with state.proxy() as data:
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_doctor_photo_again.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
            )
    else:
        async with state.proxy() as data:
            # create unique photo file name
            all_files = listdir(PHOTO_GALLERY_PATH)
            file_name = str(uuid.uuid4().hex) + PHOTO_EXTENSION
            while file_name in all_files:
                file_name = str(uuid.uuid4().hex) + PHOTO_EXTENSION
            # save photo in the gallery
            await message.document.download(PHOTO_GALLERY_PATH + file_name)
            # save obtained answer into FSM memory
            data['photo'] = file_name[:-len(PHOTO_EXTENSION)]
            # delete answer
            await message.delete()
            # ask to enter description
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_doctor_description.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
            )
        # set bot to the description state
        await FSMCreateDoctor.next()

    return


async def get_description(message: types.Message, state: FSMContext):
    # annotation
    description: List[str]

    # process the input
    description = process_input(string=message.text, delimiter=',')
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['description'] = ', '.join(description)
        # delete answer
        await message.delete()
        # ask if admin wants to provide experience
        await bot.edit_message_text(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            text=BotMessageText.ask_to_choose_experience.value,
            parse_mode='HTML',
            reply_markup=experience_specification
        )
    # set bot to the experience choice state
    await FSMCreateDoctor.next()

    return


async def get_experience_choice(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    answer: str

    # get the choice
    answer = callback_query.data.split(Symbols.separator.value)[1]
    # check the answer
    if answer == CallbackData.yes.value:
        # ask to enter experience
        await callback_query.message.edit_text(
            text=BotMessageText.ask_doctor_experience.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )
        # set bot to the experience state
        await FSMCreateDoctor.next()
    else:
        async with state.proxy() as data:
            # save obtained answer into the FSM dictionary
            data['experience'] = None
        # ask to provide science degree
        await callback_query.message.edit_text(
            text=BotMessageText.ask_doctor_science_degree.value,
            parse_mode='HTML',
            reply_markup=science_degrees_list,
        )
        # set bot to the science degree state
        await FSMCreateDoctor.science_degree.set()

    return


async def get_experience(message: types.Message, state: FSMContext):
    # validate input
    if not check_integer(message.text):
        # delete answer
        await message.delete()
        async with state.proxy() as data:
            # ask to enter experience in integer format
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_doctor_experience_again.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
            )
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['experience'] = int(message.text)
        # delete message
        await message.delete()
        # ask to choose science degree
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=data['last_msg_id'],
            text=BotMessageText.ask_doctor_science_degree.value,
            parse_mode='HTML',
            reply_markup=science_degrees_list
        )
        # set bot to the science degree state
        await FSMCreateDoctor.next()

    return


async def get_science_degree(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    science_degree: Optional[str]

    # get science degree
    science_degree = callback_query.data.split(Symbols.separator.value)[1]
    # identify science degree choice
    science_degree = None if science_degree == CallbackData.no_specification.value else science_degree
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['science_degree'] = science_degree
    # ask to choose qualification category
    await callback_query.message.edit_text(
        text=BotMessageText.ask_doctor_qual_category.value,
        parse_mode='HTML',
        reply_markup=qual_categories_list
    )
    # set bot to the qualification category state
    await FSMCreateDoctor.next()

    return


async def get_qual_category(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    qual_category: Optional[str]

    # get qualification category
    qual_category = callback_query.data.split(Symbols.separator.value)[1]
    # identify science degree choice
    qual_category = None if qual_category == CallbackData.no_specification.value else qual_category
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['qual_category'] = qual_category
        # initialize prices array
        data['price'] = []
        # set bot to the price state
        await FSMCreateDoctor.next()
        # control entering prices
        data['no_price'] = data['specialities'].copy()
        # ask to enter price
        await callback_query.message.edit_text(
            text=BotMessageText.ask_doctor_price(speciality=data['no_price'][0]),
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.doctors_settings.value)
        )

    return


async def get_price(message: types.Message, state: FSMContext):
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
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['price'].append(int(message.text))
            # delete speciality with obtained price
            del data['no_price'][0]
            # delete answer
            await message.delete()
            # check if there are any specialities without price left
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
                # delete answer (because it's impossible to edit messages when you need to attach photo)
                await bot.delete_message(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id']
                )
                # ask to confirm doctor creation
                path = PHOTO_GALLERY_PATH + data['photo'] + PHOTO_EXTENSION
                with open(path, 'rb') as photo:
                    bot_message = await bot.send_photo(
                        chat_id=data['user_uid'],
                        photo=photo,
                        caption=BotMessageText.doctor_info(
                            full_name=data['name'],
                            description=data['description'],
                            experience=data['experience'],
                            science_degree=data['science_degree'],
                            qual_category=data['qual_category'],
                            price=data['price'],
                            speciality=data['specialities']
                        ),
                        parse_mode='HTML',
                        reply_markup=confirmation_menu(section=CallbackData.doctors_settings.value)
                    )
                    # save message id
                    data['last_msg_id'] = bot_message.message_id
        # set bot to the confirmation state
        await FSMCreateDoctor.next()

    return


async def get_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]
    cache_update_required: bool
    bot_message: types.Message

    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # check user access
    if user_uid == MASTER_ADMIN or user_uid in admins:
        # set the flag to understand if it is needed to update cache
        cache_update_required = False
        async with state.proxy() as data:
            for speciality in data['specialities']:
                # check if speciality is new
                if speciality not in data['specialities_pool'].values():
                    # create speciality
                    await query.create_speciality(title=speciality)
                    # log the speciality creation
                    logger.info(f'admin {user_uid} created speciality "{speciality}"')
                    # change flag
                    cache_update_required = True
                # add doctor to the db
                await query.create_doctor(
                    full_name=data['name'],
                    photo=data['photo'],
                    description=data['description'],
                    speciality_title=speciality,
                    experience=data['experience'],
                    science_degree=data['science_degree'],
                    qual_category=data['qual_category'],
                    price=data['price'][data['specialities'].index(speciality)]
                )
            # log the doctor creation
            logger.info(
                f'admin {user_uid} created doctor "{data["name"]}" with specialities "{", ".join(data["specialities"])}"')
            # delete message (because it's impossible to edit messages when you need to unpin photo)
            await bot.delete_message(
                chat_id=user_uid,
                message_id=data['last_msg_id']
            )
            # send the "success message"
            bot_message = await bot.send_message(
                chat_id=user_uid,
                text=BotMessageText.successful_doctor_creation.value
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
            # set pause (give time to read)
            await asyncio.sleep(2)
            # check if it is needed to update cache
            if cache_update_required:
                # update specialities in cache
                await update_cache(CacheKeys.specialities.value)
            # move back to menu
            await bot.edit_message_text(
                chat_id=user_uid,
                message_id=data['last_msg_id'],
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
        create_doctor,
        lambda x: x.data and x.data == CallbackData.create_doctor.value,
        state='*'
    )
    dp.register_callback_query_handler(
        create_new_specialities,
        lambda x: x.data and x.data == CallbackData.new_specialities.value,
        state=FSMCreateDoctor.speciality
    )
    dp.register_message_handler(
        get_new_specialities,
        state=FSMCreateDoctor.speciality
    )
    dp.register_callback_query_handler(
        choose_specialities,
        lambda x: x.data and x.data.startswith(CallbackData.speciality_title.value),
        state=FSMCreateDoctor.speciality
    )
    dp.register_callback_query_handler(
        get_specialities,
        lambda x: x.data and x.data == CallbackData.selection_completed.value,
        state=FSMCreateDoctor.speciality
    )
    dp.register_message_handler(
        get_name,
        state=FSMCreateDoctor.name
    )
    dp.register_message_handler(
        get_photo,
        state=FSMCreateDoctor.photo,
        content_types=types.ContentType.ANY
    )
    dp.register_message_handler(
        get_description,
        state=FSMCreateDoctor.description
    )
    dp.register_callback_query_handler(
        get_experience_choice,
        lambda x: x.data and x.data.startswith(CallbackData.experience.value),
        state=FSMCreateDoctor.experience_choice
    )
    dp.register_message_handler(
        get_experience,
        state=FSMCreateDoctor.experience
    )
    dp.register_callback_query_handler(
        get_science_degree,
        lambda x: x.data and x.data.startswith(CallbackData.choose_science_degree.value),
        state=FSMCreateDoctor.science_degree
    )
    dp.register_callback_query_handler(
        get_qual_category,
        lambda x: x.data and x.data.startswith(CallbackData.choose_qual_category.value),
        state=FSMCreateDoctor.qual_category
    )
    dp.register_message_handler(
        get_price,
        state=FSMCreateDoctor.price
    )
    dp.register_callback_query_handler(
        create_doctor,
        lambda x: x.data and x.data == CallbackData.change_choice.value,
        state=FSMCreateDoctor.confirmation
    )
    dp.register_callback_query_handler(
        get_confirmation,
        lambda x: x.data and x.data == CallbackData.confirmation.value,
        state=FSMCreateDoctor.confirmation
    )

    return
