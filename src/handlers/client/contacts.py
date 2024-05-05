from aiogram import types, Dispatcher

from src.core.config import bot
from src.core.enums import BotMessageText, CallbackData
from src.keyboards import back_to_menu


async def show_contacts(callback_query: types.CallbackQuery):
    # send all the contacts and links that the company has
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=BotMessageText.contacts.value,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=back_to_menu(section=CallbackData.main_menu.value)
    )

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        show_contacts,
        lambda x: x.data and x.data == CallbackData.show_contacts.value,
        state='*'
    )

    return
