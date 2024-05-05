from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

from src.core.config import bot
from src.core.enums import (
    CallbackData, CacheKeys, Symbols,
    AdminPrivilegeType, BotMessageText
)
from src.core.processing import process_input
from src.core.secrets import MASTER_ADMIN
from src.core.validation import check_integer
from src.db import query
from src.keyboards import (
    admin_panel_menu, admins_config_menu, privilege_type,
    back_to_menu, main_menu_client, confirmation_menu
)
from src.keyboards.navigation import check_access
from src.utils.cache import get_cache, update_cache
from src.utils.misc import logger


# define finite-state machine
class FSMCreateAdmin(StatesGroup):
    uid = State()
    name = State()
    privilege_type = State()
    confirmation = State()


async def create_admin(callback_query: types.CallbackQuery, state: FSMContext):
    # exit FSM (if not finished)
    await state.finish()
    # check user access
    if await check_access(user_uid=callback_query.from_user.id):
        # ask to enter telegram uid
        await callback_query.message.edit_text(
            text=BotMessageText.ask_uid.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.admins.value)
        )
        # set the first state (enter FSM)
        await FSMCreateAdmin.uid.set()
        # save message id and user uid
        async with state.proxy() as data:
            data['last_msg_id'] = callback_query.message.message_id
            data['user_uid'] = callback_query.from_user.id
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.admins.value)
        )

    return


async def get_uid(message: types.Message, state: FSMContext):
    # annotation
    admins: List[int]
    uid: int

    # validate input
    if not check_integer(message.text):
        # delete answer
        await message.delete()
        async with state.proxy() as data:
            # ask to enter telegram uid in the correct form
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_uid_again.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.admins.value)
            )
    else:
        # get admins from the db
        admins = await query.get_admins_ids()
        # get admin uid
        uid = int(message.text)
        # delete answer
        await message.delete()
        # check if admin already exists
        if uid in admins:
            async with state.proxy() as data:
                # inform that this admin already exists
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.admin_already_exists.value
                )
                # set pause (give time to read)
                await asyncio.sleep(2)
                # move back to menu
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.menu_desc(),
                    parse_mode='HTML',
                    reply_markup=admins_config_menu
                )
            # exit FSM
            await state.finish()
        else:
            async with state.proxy() as data:
                # save obtained answer in the FSM memory
                data['uid'] = uid
                # ask to enter name
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.ask_admin_name.value,
                    parse_mode='HTML',
                    reply_markup=back_to_menu(section=CallbackData.admins.value)
                )
            # set bot to the name state
            await FSMCreateAdmin.next()

    return


async def get_name(message: types.Message, state: FSMContext):
    # annotation
    name: List[str]

    # process the input
    name = process_input(string=message.text, delimiter=' ')
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['name'] = ' '.join(name)
    # check admin level
    if message.from_user.id != MASTER_ADMIN:
        # delete answer
        await message.delete()
        async with state.proxy() as data:
            # save obtained answer into FSM memory
            data['privilege_type'] = AdminPrivilegeType.low.value
            # ask to confirm admin creation
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.confirm_creation(
                    uid=data['uid'],
                    name=data['name']
                ),
                parse_mode='HTML',
                reply_markup=confirmation_menu(section=CallbackData.admins.value)
            )
        # set bot to the confirmation state
        await FSMCreateAdmin.confirmation.set()
    else:
        # delete message
        await message.delete()
        async with state.proxy() as data:
            # ask to choose privilege type
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_privilege_type.value,
                reply_markup=privilege_type
            )
        # set bot to the privilege type state
        await FSMCreateAdmin.next()

    return


async def get_priv_type(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    priv_type: str

    # get privilege type
    priv_type = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['privilege_type'] = priv_type
        # ask to confirm admin creation
        await bot.edit_message_text(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            text=BotMessageText.confirm_creation(
                uid=data['uid'],
                name=data['name'],
                privilege_type=priv_type
            ),
            parse_mode='HTML',
            reply_markup=confirmation_menu(section=CallbackData.admins.value)
        )
    # set bot to the confirmation state
    await FSMCreateAdmin.next()

    return


async def get_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[int]

    # get user uid
    user_uid = callback_query.from_user.id
    # check user access
    if await check_access(user_uid=user_uid):
        async with state.proxy() as data:
            # add admin to the db
            await query.create_admin(
                user_uid=data["uid"],
                full_name=data['name'],
                privilege_type=data['privilege_type']
            )
            # log the admin creation
            logger.info(
                f'admin {user_uid} created {data["privilege_type"]} privilege admin with id {data["uid"]} '
                f'and with name "{data["name"]}"'
            )
        # send the "success message"
        await callback_query.message.edit_text(text=BotMessageText.successful_admin_creation.value)
        # set pause (give time to read)
        await asyncio.sleep(2)
        # update admins in cache
        await update_cache(CacheKeys.priv_admins.value, CacheKeys.admins.value)
        # move back to menu
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=admins_config_menu
        )
    else:
        # get admins
        admins = await get_cache(key=CacheKeys.admins.value)
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(text=BotMessageText.lack_of_privileges.value)
        # set pause (give time to read)
        await asyncio.sleep(2)
        # move back to menu
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=admin_panel_menu if user_uid in admins else main_menu_client
        )
    # exit FSM
    await state.finish()

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        create_admin,
        lambda x: x.data and x.data == CallbackData.create_admin.value,
        state='*'
    )
    dp.register_message_handler(
        get_uid,
        state=FSMCreateAdmin.uid
    )
    dp.register_message_handler(
        get_name,
        state=FSMCreateAdmin.name
    )
    dp.register_callback_query_handler(
        get_priv_type,
        lambda x: x.data and x.data.startswith(CallbackData.privilege.value),
        state=FSMCreateAdmin.privilege_type
    )
    dp.register_callback_query_handler(
        create_admin,
        lambda x: x.data and x.data == CallbackData.change_choice.value,
        state=FSMCreateAdmin.confirmation
    )
    dp.register_callback_query_handler(
        get_confirmation,
        lambda x: x.data and x.data == CallbackData.confirmation.value,
        state=FSMCreateAdmin.confirmation
    )

    return
