from typing import Any, List

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import asyncio

from src.core.enums import (
    CallbackData, Symbols, CacheKeys,
    BotMessageText, AdminPrivilegeType
)
from src.core.secrets import MASTER_ADMIN
from src.db import query
from src.keyboards import (
    admins_config_menu, show_admins, confirmation_menu,
    admin_panel_menu, main_menu_client, back_to_menu
)
from src.keyboards.navigation import check_access
from src.utils.cache import get_cache, update_cache
from src.utils.misc import logger


# define finite-state machine
class FSMDeleteAdmin(StatesGroup):
    admins = State()
    confirmation = State()


async def delete_admin(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    user_uid: int
    admins: List[Any]

    # exit FSM (if not finished)
    await state.finish()
    # get user uid
    user_uid = callback_query.from_user.id
    # check user access
    if await check_access(user_uid=user_uid):
        # get admins basing on the current admin type
        admins = await query.get_admins() if user_uid == MASTER_ADMIN \
            else await query.get_admins(privilege_type=AdminPrivilegeType.low.value)
        # set the first state (enter FSM)
        await FSMDeleteAdmin.admins.set()
        async with state.proxy() as data:
            # save message id and user uid
            data['last_msg_id'] = callback_query.message.message_id
            data['user_uid'] = user_uid
            # crate dictionaries to optimize callback_data
            data['chosen_admins'] = {}
            data['admins'] = {str(admin.user_uid): admin.full_name for admin in admins}
            # ask to choose admins for deletion
            await callback_query.message.edit_text(
                text=BotMessageText.ask_to_choose_admins.value,
                parse_mode='HTML',
                reply_markup=show_admins(
                    admins=data['admins'],
                    section=CallbackData.admins.value,
                    marked_uids=[]
                )
            )
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.admins.value)
        )

    return


async def choose_admins(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    uid: str

    # get admin uid
    uid = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # add/remove admin choice
        if uid in data['chosen_admins'].keys():
            # we use str type key as we have Redis storage which keeps data in string format
            del data['chosen_admins'][uid]
        else:
            data['chosen_admins'][uid] = data['admins'][uid]
        # mark chosen admin
        await callback_query.message.edit_reply_markup(
            reply_markup=show_admins(
                admins=data['admins'],
                section=CallbackData.admins.value,
                marked_uids=list(data['chosen_admins'].keys())
            )
        )

    return


async def get_admins(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        # ask to confirm the deletion
        await callback_query.message.edit_text(
            text=BotMessageText.confirm_deletion(employees=list(data['chosen_admins'].values())),
            parse_mode='HTML',
            reply_markup=confirmation_menu(section=CallbackData.admins.value)
        )
    # set bot to the confirmation state
    await FSMDeleteAdmin.next()

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
            for uid, name in data['chosen_admins'].items():
                # delete admin
                await query.delete_admin(user_uid=int(uid))
                # log the admin deletion
                logger.info(f'admin {user_uid} deleted admin {int(uid)} with name "{name}"')
        # send the "success message"
        await callback_query.message.edit_text(text=BotMessageText.successful_admins_deletion.value)
        # set pause (give time to read)
        await asyncio.sleep(2)
        # update admins in cache
        await update_cache(CacheKeys.admins.value, CacheKeys.priv_admins.value)
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
        delete_admin,
        lambda x: x.data and x.data == CallbackData.delete_admin.value,
        state='*'
    )
    dp.register_callback_query_handler(
        choose_admins,
        lambda x: x.data and x.data.startswith(CallbackData.choose_person.value),
        state=FSMDeleteAdmin.admins
    )
    dp.register_callback_query_handler(
        get_admins,
        lambda x: x.data and x.data == CallbackData.selection_completed.value,
        state=FSMDeleteAdmin.admins
    )
    dp.register_callback_query_handler(
        delete_admin,
        lambda x: x.data and x.data == CallbackData.change_choice.value,
        state=FSMDeleteAdmin.confirmation
    )
    dp.register_callback_query_handler(
        get_confirmation,
        lambda x: x.data and x.data == CallbackData.confirmation.value,
        state=FSMDeleteAdmin.confirmation
    )

    return
