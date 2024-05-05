from typing import Optional, List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.core.config import bot
from src.core.enums import BotMessageText, CacheKeys, ButtonText
from src.core.secrets import MASTER_ADMIN
from src.keyboards import main_menu_client, main_menu_admin
from src.utils.cache import get_cache


async def start(message: types.Message, state: FSMContext):
    # annotation
    user_uid: int
    cur_state: Optional[str]
    admins: List[int]

    # get user uid
    user_uid = message.from_user.id
    # get current state
    cur_state = await state.get_state()
    # check state
    if cur_state:
        # delete messages (if there are any)
        await del_messages(
            chat_id=user_uid,
            state=state
        )
    # exit FSM (if not finished)
    await state.finish()
    # delete "/start" command from the chat
    await message.delete()
    # get admins
    admins = await get_cache(key=CacheKeys.admins.value)
    # send main menu
    await bot.send_message(
        chat_id=user_uid,
        text=BotMessageText.menu_desc(instruction=True),
        parse_mode='HTML',
        reply_markup=main_menu_admin if (
                user_uid == MASTER_ADMIN or user_uid in admins
        ) else main_menu_client
    )

    return


async def del_messages(chat_id: int, state: FSMContext) -> None:
    async with state.proxy() as data:
        # try to delete last message
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=data['last_msg_id']
            )
        except:
            # try to remove reply_markup from the last message
            try:
                await bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=data['last_msg_id'],
                    reply_markup=None
                )
            except:
                pass
        # try to delete additional messages
        try:
            for msg_id in data['messages_to_del']:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=msg_id
                )
        except:
            pass

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        start,
        commands=['старт', 'start'],
        state='*'
    )
    dp.register_message_handler(
        start,
        lambda msg: msg.text.lower() in ['старт', 'start', 'меню', 'menu', ButtonText.start.value.lower()],
        state='*'
    )

    return
