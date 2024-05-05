from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

from src.core.config import bot
from src.core.enums import BotMessageText, CallbackData, CacheKeys
from src.core.secrets import CHAT_ID, MASTER_ADMIN
from src.db.query import create_feedback
from src.keyboards import main_menu_client, back_to_menu, main_menu_admin
from src.utils.cache import get_cache


# define finite-state machine
class FSMFeedback(StatesGroup):
    feedback = State()


async def leave_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    # exit FSM (if not finished)
    await state.finish()
    # ask to enter feedback
    await callback_query.message.edit_text(
        text=BotMessageText.ask_feedback.value,
        parse_mode='HTML',
        reply_markup=back_to_menu(section=CallbackData.main_menu.value)
    )
    # set the first state
    await FSMFeedback.feedback.set()
    # save message id and user uid
    async with state.proxy() as data:
        data['last_msg_id'] = callback_query.message.message_id
        data['user_uid'] = callback_query.from_user.id

    return


async def get_message(message: types.Message, state: FSMContext):
    # annotation
    admins: List[int]

    async with state.proxy() as data:
        # save obtained answer and user info in the FSM memory
        data['message'] = message.text
        data['username'] = message.from_user.username
        data['full_name'] = message.from_user.full_name
        # send feedback to the group/channel with specified ID
        await bot.send_message(
            chat_id=CHAT_ID,
            text=BotMessageText.feedback_request(details=data),
            parse_mode='HTML'
        )
        # add new feedback to the db
        await create_feedback(
            tg_uid=data['user_uid'],
            username=data['username'],
            message=data['message']
        )
        # remove reply_markup
        await bot.edit_message_reply_markup(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            reply_markup=None
        )
        # send the "success message"
        bot_message = await bot.send_message(
            chat_id=data['user_uid'],
            text=BotMessageText.confirm_feedback_success.value,
            parse_mode='HTML'
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
        leave_feedback,
        lambda x: x.data and x.data == CallbackData.leave_feedback.value,
        state='*'
    )
    dp.register_message_handler(
        get_message,
        state=FSMFeedback.feedback
    )

    return
