from typing import List, Dict

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from src.core.enums import (
    Numbers, ButtonText, Symbols,
    NavigationType, CallbackData
)

"""
----------------------------------------------------
BUTTONS
----------------------------------------------------
"""
start = KeyboardButton(ButtonText.start.value)
user_contact = KeyboardButton(
    text=ButtonText.user_contact.value,
    request_contact=True,
    one_time_keyboard=True
)
appointment_form = InlineKeyboardButton(
    text=ButtonText.appointment_form.value,
    callback_data=CallbackData.appointment_request.value
)
callback_form = InlineKeyboardButton(
    text=ButtonText.callback_form.value,
    callback_data=CallbackData.callback_request.value
)
feedback = InlineKeyboardButton(
    text=ButtonText.feedback.value,
    callback_data=CallbackData.leave_feedback.value
)
contacts = InlineKeyboardButton(
    text=ButtonText.contacts.value,
    callback_data=CallbackData.show_contacts.value
)
instruction = InlineKeyboardButton(
    text=ButtonText.instruction.value,
    callback_data=CallbackData.send_instruction.value
)
online = InlineKeyboardButton(
    text=ButtonText.online.value,
    callback_data=CallbackData.choose_online.value
)
offline = InlineKeyboardButton(
    text=ButtonText.offline.value,
    callback_data=CallbackData.choose_offline.value
)
call = InlineKeyboardButton(
    text=ButtonText.call.value,
    callback_data=CallbackData.choose_call.value
)
chat = InlineKeyboardButton(
    text=ButtonText.chat.value,
    callback_data=CallbackData.choose_chat.value
)
pay = InlineKeyboardButton(
    text=ButtonText.pay.value,
    callback_data=CallbackData.initialize_payment.value
)
yes = InlineKeyboardButton(
    text=ButtonText.yes.value,
    callback_data=CallbackData.yes.value
)
no = InlineKeyboardButton(
    text=ButtonText.no.value,
    callback_data=CallbackData.no.value
)


def back_to_menu_btn(section: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=ButtonText.back_to_menu.value,
        callback_data=CallbackData.back_to_menu.value + Symbols.separator.value + section
    )


def create_next_button(page: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=ButtonText.next.value,
                                callback_data=CallbackData.next.value + Symbols.separator.value + str(page + 1))


def create_prev_button(page: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=ButtonText.prev.value,
                                callback_data=CallbackData.prev.value + Symbols.separator.value + str(page - 1))


"""
----------------------------------------------------
KEYBOARDS
----------------------------------------------------
"""
main_menu_client = InlineKeyboardMarkup(row_width=1) \
    .add(callback_form) \
    .add(appointment_form) \
    .add(feedback) \
    .add(contacts) \
    .add(instruction)

share_contact = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) \
    .add(user_contact) \
    .add(start)

consultation_type = InlineKeyboardMarkup(row_width=2) \
    .row(offline, online) \
    .add(back_to_menu_btn(section=CallbackData.main_menu.value))

communication_type = InlineKeyboardMarkup(row_width=2) \
    .row(call, chat) \
    .add(back_to_menu_btn(section=CallbackData.main_menu.value))

payment = InlineKeyboardMarkup(row_width=1) \
    .add(pay) \
    .add(back_to_menu_btn(section=CallbackData.main_menu.value))

yes_no_kb = InlineKeyboardMarkup(row_width=2) \
    .row(yes, no) \
    .add(back_to_menu_btn(section=CallbackData.main_menu.value))


def choose_doctor(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1) \
        .add(InlineKeyboardButton(text=ButtonText.choose_doctor.value,
                                  callback_data=callback_data))


def generate_speciality_buttons(specialities: Dict[str, str], index_2: int,
                                index_1: int = 0) -> List[InlineKeyboardButton]:
    return [InlineKeyboardButton(
        text=specialities[str(i)],
        callback_data=CallbackData.speciality_title.value + Symbols.separator.value + str(i)
    ) for i in range(index_1, index_2)]


def generate_speciality_menu(speciality_buttons: List[InlineKeyboardButton],
                             page: int = None, nav_type: str = None) -> InlineKeyboardMarkup:
    if nav_type == NavigationType.next.value:
        return InlineKeyboardMarkup(row_width=Numbers.specialities_in_row.value) \
            .add(*speciality_buttons) \
            .insert(create_next_button(page)) \
            .add(back_to_menu_btn(section=CallbackData.main_menu.value))
    elif nav_type == NavigationType.prev.value:
        return InlineKeyboardMarkup(row_width=Numbers.specialities_in_row.value) \
            .add(*speciality_buttons) \
            .add(create_prev_button(page)) \
            .add(back_to_menu_btn(section=CallbackData.main_menu.value))
    elif nav_type == NavigationType.prev_next.value:
        return InlineKeyboardMarkup(row_width=Numbers.specialities_in_row.value) \
            .add(*speciality_buttons) \
            .row(create_prev_button(page),
                 create_next_button(page)) \
            .add(back_to_menu_btn(section=CallbackData.main_menu.value))
    else:
        return InlineKeyboardMarkup(row_width=Numbers.specialities_in_row.value) \
            .add(*speciality_buttons) \
            .add(back_to_menu_btn(section=CallbackData.main_menu.value))


def back_to_menu(section: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1) \
        .add(back_to_menu_btn(section=section))
