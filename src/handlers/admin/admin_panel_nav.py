from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.core.config import bot
from src.core.enums import (
    CallbackData, Symbols,
    BotMessageText, CacheKeys
)
from src.core.secrets import MASTER_ADMIN
from src.keyboards import step_back
from src.keyboards.navigation import (
    admin_pages, admin_nav, doctors_settings_menu,
    check_access, privilege_pages, client_nav
)
from src.utils.cache import get_cache


async def admin_menu_navigation(callback_query: types.CallbackQuery):
    # annotation
    user_uid: int
    admins: List[int]
    page: str

    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # get the requested page
    page = callback_query.data.split(Symbols.separator.value)[1]
    # check page and user status
    if (
            page in privilege_pages and await check_access(user_uid=user_uid)
            or (
                (page in admin_pages or page == CallbackData.main_menu.value)
                and (user_uid in admins or user_uid == MASTER_ADMIN)
            )
    ):
        # change the page
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=admin_nav[page]
        )
    elif user_uid in admins:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=step_back(section=CallbackData.admin_panel.value)
        )
    else:
        # change the page
        await callback_query.message.edit_text(
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=client_nav[CallbackData.main_menu.value]
        )

    return


async def moving_back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    # try to delete additional messages if needed
    try:
        async with state.proxy() as data:
            for msg_id in data['messages_to_del']:
                await bot.delete_message(
                    chat_id=callback_query.from_user.id,
                    message_id=msg_id
                )
    except:
        pass
    # exit FSM (if not finished)
    await state.finish()
    # check content type
    if callback_query.message.content_type == 'photo':
        # delete message
        await callback_query.message.delete()
        # send the menu
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=BotMessageText.menu_desc(),
            parse_mode='HTML',
            reply_markup=doctors_settings_menu
        )
    else:
        await admin_menu_navigation(callback_query=callback_query)

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        admin_menu_navigation,
        lambda x: x.data and x.data.startswith(CallbackData.admin_menu_nav.value),
        state='*'
    )
    dp.register_callback_query_handler(
        moving_back_to_menu,
        lambda x: x.data and x.data.startswith(CallbackData.back_to_menu.value),
        state='*'
    )

    return
