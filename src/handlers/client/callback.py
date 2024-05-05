from typing import List
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

from src.core.config import bot
from src.core.enums import BotMessageText, CallbackData, CacheKeys
from src.core.processing import process_input, standardize_phone
from src.core.secrets import CHAT_ID, MASTER_ADMIN
from src.core.validation import check_phone
from src.db.query import create_callback
from src.keyboards import (
    share_contact, main_menu_client,
    back_to_menu, main_menu_admin
)
from src.utils.cache import get_cache


# define finite-state machine
class FSMCallback(StatesGroup):
    name = State()
    phone = State()


async def fill_form(callback_query: types.CallbackQuery, state: FSMContext):
    # exit FSM (if not finished)
    await state.finish()
    # ask to enter name
    await callback_query.message.edit_text(
        text=BotMessageText.ask_name(
            section=CallbackData.callback_request.value,
            stage='1/2'
        ),
        parse_mode='HTML',
        reply_markup=back_to_menu(section=CallbackData.main_menu.value)
    )
    # set the first state
    await FSMCallback.name.set()
    # save message id and user uid
    async with state.proxy() as data:
        data['last_msg_id'] = callback_query.message.message_id
        data['user_uid'] = callback_query.from_user.id

    return


async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # save obtained answer into the FSM memory
        data['name'] = ' '.join(process_input(string=message.text, delimiter=' '))
        # remove rely_markup
        await bot.edit_message_reply_markup(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            reply_markup=None
        )
        # ask to enter phone
        bot_message = await bot.send_message(
            chat_id=data['user_uid'],
            text=BotMessageText.ask_phone(
                section=CallbackData.callback_request.value,
                stage='2/2'
            ),
            parse_mode='HTML',
            reply_markup=share_contact
        )
        # update message id
        data['last_msg_id'] = bot_message.message_id
    # set bot to the next state
    await FSMCallback.next()

    return


async def get_phone(message: types.Message, state: FSMContext):
    # annotation
    clean_phone: str
    admins: List[int]

    # process input leaving only numbers
    try:
        clean_phone = re.sub(r'\D', '', message.text)
    except TypeError:
        pass
    # phone number validation
    if (
            message.content_type == 'text'
            and not check_phone(clean_phone)
    ):
        async with state.proxy() as data:
            # ask to enter phone in the correct form
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_phone(
                    section=CallbackData.callback_request.value,
                    stage='2/2',
                    again=True
                ),
                parse_mode='HTML',
                reply_markup=share_contact
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            if message.content_type == 'contact':
                data['phone'] = message.contact.phone_number
            else:
                data['phone'] = standardize_phone(clean_phone)
            # send request to the telegram group/channel with specified ID
            await bot.send_message(
                chat_id=CHAT_ID,
                text=BotMessageText.callback_request(data),
                parse_mode='HTML'
            )
            # add new callback to the db
            await create_callback(
                tg_uid=data['user_uid'],
                username=message.from_user.username,
                full_name=data['name'],
                phone=data['phone']
            )
            # send the "success message"
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.confirm_request_success.value,
                parse_mode='HTML',
                reply_markup=types.ReplyKeyboardRemove()
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
            # set pause (give time to read)
            await asyncio.sleep(4)
            # get admins
            admins = await get_cache(key=CacheKeys.admins.value)
            # move back to menu
            await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.menu_desc(),
                parse_mode='HTML',
                reply_markup=main_menu_admin if (
                        data['user_uid'] in admins or data['user_uid'] == MASTER_ADMIN
                ) else main_menu_client
            )
        # exit FSM
        await state.finish()

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        fill_form,
        lambda x: x.data and x.data == CallbackData.callback_request.value,
        state='*'
    )
    dp.register_message_handler(
        get_name,
        state=FSMCallback.name
    )
    dp.register_message_handler(
        get_phone,
        state=FSMCallback.phone,
        content_types=[types.ContentType.CONTACT, types.ContentType.TEXT]
    )

    return
