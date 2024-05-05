from typing import List

from aiogram import types, Dispatcher

from src.core.config import bot
from src.core.enums import BotMessageText, CallbackData, CacheKeys
from src.core.secrets import MASTER_ADMIN
from src.keyboards import main_menu_client, main_menu_admin
from src.utils.cache import get_cache


async def send_instruction(callback_query: types.CallbackQuery):
    # annotate variables
    user_uid: int
    admins: List[int]

    # get user uid
    user_uid = callback_query.from_user.id
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # send instruction
    await callback_query.message.edit_text(
        text=BotMessageText.instruction.value,
        parse_mode='HTML'
    )
    # send menu
    await bot.send_message(
        chat_id=user_uid,
        text=BotMessageText.menu_desc(instruction=False),
        parse_mode='HTML',
        reply_markup=main_menu_admin if (
                user_uid == MASTER_ADMIN or user_uid in admins
        ) else main_menu_client
    )

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        send_instruction,
        lambda x: x.data and x.data == CallbackData.send_instruction.value,
        state='*'
    )

    return
