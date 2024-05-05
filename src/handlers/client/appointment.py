from typing import Any, List, Union
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
import asyncio

from src.core.config import bot
from src.core.enums import (
    CommunicationType, BotMessageText, CallbackData, Symbols,
    ConsultationType, Numbers, Payment, NavigationType, CacheKeys
)
from src.core.processing import process_input, standardize_phone
from src.core.secrets import (
    CHAT_ID, MASTER_ADMIN, YOOKASSA_TOKEN,
    PHOTO_GALLERY_PATH, PHOTO_EXTENSION
)
from src.core.validation import check_phone
from src.db.query import (
    create_appointment, get_doctors_by_speciality, get_price
)
from src.keyboards import (
    consultation_type, share_contact, communication_type,
    choose_doctor, generate_speciality_buttons, payment,
    generate_speciality_menu, yes_no_kb, main_menu_client,
    back_to_menu, main_menu_admin
)
from src.parsers import generate_link
from src.utils.cache import get_cache


# define finite-state machine
class FSMAppointment(StatesGroup):
    consultation_type = State()
    user_request = State()
    datetime_choice = State()
    datetime = State()
    communication_type = State()
    phone = State()
    name = State()
    payment = State()
    link = State()


async def fill_form(callback_query: types.CallbackQuery, state: FSMContext):
    # exit FSM (if not finished)
    await state.finish()
    # ask to choose consultation type
    await callback_query.message.edit_text(
        text=BotMessageText.ask_cons_type.value,
        parse_mode='HTML',
        reply_markup=consultation_type
    )
    # set the first state
    await FSMAppointment.consultation_type.set()
    # save message id and user uid
    async with state.proxy() as data:
        data['last_msg_id'] = callback_query.message.message_id
        data['user_uid'] = callback_query.from_user.id
        data['messages_to_del'] = []

    return


async def get_cons_type(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    specialities: List[str]
    speciality_buttons: List[InlineKeyboardButton]
    page: int

    # check the chosen type
    if callback_query.data == CallbackData.choose_offline.value:
        # save obtained answer in the FSM memory
        async with state.proxy() as data:
            data['consultation_type'] = ConsultationType.offline.value
            data['n_steps'] = '/4'
        # ask to enter specialist/service needed
        await callback_query.message.edit_text(
            text=BotMessageText.ask_request.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.main_menu.value)
        )
    else:
        # get all available specialities
        specialities = await get_cache(key=CacheKeys.specialities.value)
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['consultation_type'] = ConsultationType.online.value
            data['n_steps'] = '/5'
            data['specialities'] = {str(key): value for key, value in enumerate(specialities)}
            data['n_spec'] = len(data['specialities'])
            # check the number of specialities available
            if data['n_spec'] <= Numbers.specialities_per_page.value:
                # generate specialities buttons
                speciality_buttons = generate_speciality_buttons(specialities=data['specialities'],
                                                                 index_2=data['n_spec'])
                # show specialities menu
                await callback_query.message.edit_text(
                    text=BotMessageText.ask_speciality.value,
                    parse_mode='HTML',
                    reply_markup=generate_speciality_menu(speciality_buttons=speciality_buttons)
                )
            else:
                # generate specialities buttons
                speciality_buttons = generate_speciality_buttons(specialities=data['specialities'],
                                                                 index_2=Numbers.specialities_per_page.value)
                # set the page number
                page = 0
                # show specialities menu
                await callback_query.message.edit_text(
                    text=BotMessageText.ask_speciality.value,
                    parse_mode='HTML',
                    reply_markup=generate_speciality_menu(
                        speciality_buttons=speciality_buttons,
                        page=page,
                        nav_type=NavigationType.next.value
                    )
                )
    # set bot to the user request state
    await FSMAppointment.next()

    return


async def show_prev(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    page: int
    n_left: int
    speciality_buttons: List[InlineKeyboardButton]

    # get page number
    page = int(callback_query.data.split(Symbols.separator.value)[1])
    # calculate number of items on the left (from current page)
    n_left = page * Numbers.specialities_per_page.value
    async with state.proxy() as data:
        # generate specialities buttons
        speciality_buttons = generate_speciality_buttons(
            specialities=data['specialities'],
            index_2=n_left + Numbers.specialities_per_page.value,
            index_1=n_left
        )
    # show the previous page with specified navigation type
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_speciality_menu(
            speciality_buttons=speciality_buttons,
            page=page,
            nav_type=NavigationType.next.value if page == 0 else NavigationType.prev_next.value
        )
    )

    return


async def show_next(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    page: int
    n_left: int
    n_right: int
    speciality_buttons: List[InlineKeyboardButton]

    # get the page number
    page = int(callback_query.data.split(Symbols.separator.value)[1])
    # calculate the number of items on the left (from current page)
    n_left = page * Numbers.specialities_per_page.value
    async with state.proxy() as data:
        # calculate the number of items on the right (opposite to "n_left")
        n_right = data['n_spec'] - n_left
        # generate specialities buttons
        speciality_buttons = generate_speciality_buttons(
            specialities=data['specialities'],
            index_2=data['n_spec'] if n_right < Numbers.specialities_per_page.value \
                else n_left + Numbers.specialities_per_page.value,
            index_1=n_left
        )
    # show the next page with specified navigation type
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_speciality_menu(
            speciality_buttons=speciality_buttons,
            page=page,
            nav_type=NavigationType.prev.value if n_right <= Numbers.specialities_per_page.value \
                else NavigationType.prev_next.value
        )
    )

    return


async def get_speciality(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    key: str
    doctors: List[Any]
    speciality_buttons: List[InlineKeyboardButton]
    bot_message: types.Message

    # get speciality key
    key = callback_query.data.split(Symbols.separator.value)[1]
    async with state.proxy() as data:
        # try to delete messages with doctors cards if needed
        for msg_id in data['messages_to_del']:
            try:
                await bot.delete_message(
                    chat_id=data['user_uid'],
                    message_id=msg_id
                )
            except:
                pass
        data['messages_to_del'] = []
        # get the speciality title
        data['speciality_title'] = data['specialities'][key]
        # get doctors from the db with chosen speciality
        doctors = await get_doctors_by_speciality(title=data['speciality_title'])
        # specify speciality of doctors presented
        bot_message = await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=BotMessageText.chosen_speciality(speciality=data['speciality_title']),
            parse_mode='HTML'
        )
        # save message id
        data['messages_to_del'].append(bot_message.message_id)
        # create dictionary to optimize the length of callback data
        data['doc_dict'] = {}
        # show all the available doctors in chosen category
        for doctor in doctors:
            data['doc_dict'][doctor.id] = {}
            data['doc_dict'][doctor.id][CallbackData.full_name.value] = doctor.full_name
            data['doc_dict'][doctor.id][CallbackData.photo.value] = doctor.photo
            path = PHOTO_GALLERY_PATH + doctor.photo + PHOTO_EXTENSION
            with open(path, 'rb') as photo:
                bot_message = await bot.send_photo(
                    chat_id=callback_query.from_user.id,
                    photo=photo,
                    caption=BotMessageText.doctor_info(
                        full_name=doctor.full_name,
                        description=doctor.description,
                        experience=doctor.experience,
                        science_degree=doctor.science_degree,
                        qual_category=doctor.qual_category,
                        price=doctor.price
                    ),
                    parse_mode='HTML',
                    reply_markup=choose_doctor(CallbackData.doctor.value + Symbols.separator.value + str(doctor.id))
                )
                # save message id
                data['messages_to_del'].append(bot_message.message_id)

    return


async def get_request(content: Union[types.Message, types.CallbackQuery], state: FSMContext):
    # annotation
    bot_message: types.Message

    async with state.proxy() as data:
        # check input content type
        if type(content) == types.Message:
            # check consultation type
            if data['consultation_type'] == ConsultationType.online.value:
                # delete message
                await content.delete()
                # exit function
                return
            # save obtained answer in the FSM memory
            data['doctor_id'] = None
            data['user_request'] = content.text
            data['speciality_title'] = None
            # remove reply_markup
            await bot.edit_message_reply_markup(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                reply_markup=None
            )
        else:
            # save obtained answer in the FSM memory
            data['doctor_id'] = int(content.data.split(Symbols.separator.value)[1])
            # str type key as we have Redis storage which keeps data in string format
            data['user_request'] = data['doc_dict'][str(data['doctor_id'])][CallbackData.full_name.value]
            # try to delete messages with doctors cards if needed
            try:
                for msg_id in data['messages_to_del']:
                    await bot.delete_message(
                        chat_id=content.from_user.id,
                        message_id=msg_id
                    )
                # hide doctors menu and confirm choice
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.chosen_doctor(
                        doctor=data['user_request'],
                        speciality=data['speciality_title']
                    ),
                    parse_mode='HTML',
                    reply_markup=None
                )
            except:
                # remove reply_markup
                await bot.edit_message_reply_markup(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    reply_markup=None
                )
                # confirm choice
                await bot.send_message(
                    chat_id=data['user_uid'],
                    text=BotMessageText.chosen_doctor(
                        doctor=data['user_request'],
                        speciality=data['speciality_title']
                    ),
                    parse_mode='HTML'
                )
            data['messages_to_del'] = []
        # ask if user wants to specify preferable time
        bot_message = await bot.send_message(
            chat_id=data['user_uid'],
            text=BotMessageText.ask_dt_choice(stage='2' + data['n_steps']),
            parse_mode='HTML',
            reply_markup=yes_no_kb
        )
        # update message id
        data['last_msg_id'] = bot_message.message_id
    # set bot to the datetime choice state
    await FSMAppointment.next()

    return


async def get_datetime_choice(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    bot_message: types.Message

    # check answer
    if callback_query.data == CallbackData.yes.value:
        async with state.proxy() as data:
            # ask to enter preferable date/time
            await callback_query.message.edit_text(
                text=BotMessageText.ask_dt(stage='2' + data['n_steps']),
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.main_menu.value)
            )
        # set bot to the datetime state
        await FSMAppointment.next()
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['datetime'] = None
            # remove reply_markup and confirm choice
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.no_dt(stage='2' + data['n_steps']),
                parse_mode='HTML',
                reply_markup=None
            )
            # ask to choose type of communication with administrator
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_com_type(stage='3' + data['n_steps']),
                parse_mode='HTML',
                reply_markup=communication_type
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
        # set bot to the communication type state
        await FSMAppointment.communication_type.set()

    return


async def get_datetime(message: types.Message, state: FSMContext):
    # annotation
    bot_message: types.Message

    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['datetime'] = message.text
        # remove reply_markup
        await bot.edit_message_reply_markup(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            reply_markup=None
        )
        # ask to choose type of communication with administrator
        bot_message = await bot.send_message(
            chat_id=data['user_uid'],
            text=BotMessageText.ask_com_type(stage='3' + data['n_steps']),
            parse_mode='HTML',
            reply_markup=communication_type
        )
        # update message id
        data['last_msg_id'] = bot_message.message_id
    # set bot to the communication type state
    await FSMAppointment.next()

    return


async def get_com_type(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    bot_message: types.Message

    # check the chosen type
    if callback_query.data == CallbackData.choose_call.value:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['communication_type'] = CommunicationType.call.value
            # edit message with question
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.com_type_choice(
                    stage='3' + data['n_steps'],
                    com_type=data['communication_type']
                ),
                parse_mode='HTML',
                reply_markup=None
            )
            # ask to enter phone number
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_phone(
                    section=CallbackData.appointment_request.value,
                    stage='3' + data['n_steps']
                ),
                parse_mode='HTML',
                reply_markup=share_contact
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
        # set bot to the phone state
        await FSMAppointment.next()
    else:
        async with state.proxy() as data:
            # save obtained answer in the FSM memory
            data['communication_type'] = CommunicationType.chat.value
            # edit message with question
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.com_type_choice(
                    stage='3' + data['n_steps'],
                    com_type=data['communication_type']
                ),
                parse_mode='HTML',
                reply_markup=None
            )
            # set bot to the phone state
            await FSMAppointment.next()
            # check existence of username
            if not callback_query['from'].username:
                # save obtained answer in the FSM memory
                data['is_username_empty'] = True
                # ask to provide phone number instead
                bot_message = await bot.send_message(
                    chat_id=data['user_uid'],
                    text=BotMessageText.ask_phone(
                        section=CallbackData.appointment_request.value,
                        stage='3' + data['n_steps'],
                        instead=True
                    ),
                    parse_mode='HTML',
                    reply_markup=share_contact
                )
                # update message id
                data['last_msg_id'] = bot_message.message_id
                # exit function
                return
            else:
                # save obtained answer in the FSM memory
                data['is_username_empty'] = False
                data['username'] = callback_query['from'].username
                data['phone'] = None
                # ask to enter name
                bot_message = await bot.send_message(
                    chat_id=data['user_uid'],
                    text=BotMessageText.ask_name(
                        section=CallbackData.appointment_request.value,
                        stage='4' + data['n_steps']
                    ),
                    parse_mode='HTML',
                    reply_markup=back_to_menu(section=CallbackData.main_menu.value)
                )
            # update message id
            data['last_msg_id'] = bot_message.message_id
        # set bot to the name state
        await FSMAppointment.name.set()

    return


async def get_phone(message: types.Message, state: FSMContext):
    # annotation
    clean_phone: str
    bot_message: types.Message

    # process phone number if it was printed manually
    try:
        clean_phone = re.sub(r'\D', '', message.text)
    except TypeError:
        pass
    # phone number validation check
    if (
            message.content_type == 'text'
            and not check_phone(clean_phone)
    ):
        async with state.proxy() as data:
            # ask to enter phone in the correct form
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_phone(
                    section=CallbackData.appointment_request.value,
                    stage='3' + data['n_steps'],
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
            data['username'] = message.from_user.username
            if message.content_type == 'contact':
                data['phone'] = message.contact.phone_number
            else:
                data['phone'] = standardize_phone(clean_phone)
            # ask to enter name
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=BotMessageText.ask_name(
                    section=CallbackData.appointment_request.value,
                    stage='4' + data['n_steps']
                ),
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.main_menu.value)
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
        # set bot to the name state
        await FSMAppointment.next()

    return


async def get_name(message: types.Message, state: FSMContext):
    # annotation
    admins: List[int]
    bot_message: types.Message
    res: types.Message

    async with state.proxy() as data:
        # save obtained answer in the FSM memory
        data['name'] = ' '.join(process_input(string=message.text, delimiter=' '))
        data['request_message'] = BotMessageText.appointment_request(data)
        # send request to the telegram group/channel with specified ID
        res = await bot.send_message(
            chat_id=CHAT_ID,
            text=data['request_message'],
            parse_mode='HTML'
        )
        # edit message with question
        await bot.edit_message_reply_markup(
            chat_id=data['user_uid'],
            message_id=data['last_msg_id'],
            reply_markup=None
        )
        # check consultation type
        if data['consultation_type'] == ConsultationType.offline.value:
            # add new appointment to the db
            await create_appointment(
                tg_uid=data['user_uid'],
                username=data['username'],
                full_name=data['name'],
                phone=data['phone'],
                consultation_type=data['consultation_type'],
                communication_type=data['communication_type'],
                user_request=data['user_request'],
                doctor_id=data['doctor_id'],
                preferable_dt=data['datetime']
            )
            # send warning (in case of chat type and not None username)
            if data['communication_type'] == CommunicationType.chat.value and not data['is_username_empty']:
                # ask to hold username unchanged
                bot_message = await bot.send_message(
                    chat_id=data['user_uid'],
                    text=BotMessageText.username_warning.value,
                    parse_mode='HTML'
                )
                # update message id
                data['last_msg_id'] = bot_message.message_id
                # set pause (give time to read)
                await asyncio.sleep(6)
                # send the "success message"
                await bot.edit_message_text(
                    chat_id=data['user_uid'],
                    message_id=data['last_msg_id'],
                    text=BotMessageText.confirm_request_success.value,
                    parse_mode='HTML'
                )
            else:
                # send the "success message"
                bot_message = await bot.send_message(
                    chat_id=data['user_uid'],
                    text=BotMessageText.confirm_request_success.value,
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
        else:
            # save request message id for editing
            data['request_msg_id'] = res.message_id
            # set bot to the next state
            await FSMAppointment.next()
            # ask to pay and provide instruction (future steps)
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=Payment.instruction.value,
                parse_mode='HTML',
                reply_markup=payment
            )
            # update message id
            data['last_msg_id'] = bot_message.message_id
            # exit function
            return
    # exit FSM
    await state.finish()

    return


async def start_payment(callback_query: types.CallbackQuery, state: FSMContext):
    # annotation
    price: int
    bill: types.Invoice

    async with state.proxy() as data:
        # get the price of the consultation
        price = await get_price(
            photo=data['doc_dict'][str(data['doctor_id'])][CallbackData.photo.value],
            speciality=data['speciality_title']
        )
        # save the price
        data['price'] = price
        # generate and send payment bill
        bill = await bot.send_invoice(
            chat_id=data['user_uid'],
            title=Payment.title.value,
            description=f'{data["user_request"]} ({data["speciality_title"]})',
            payload=Payment.appointment.value,
            provider_token=YOOKASSA_TOKEN,
            currency=Payment.currency.value,
            start_parameter=f'{Payment.prefix.value}{callback_query.from_user.id}',
            prices=[{
                'label': Payment.label.value,
                'amount': price * 100  # *100 is needed to include cents (копейки)
            }]
        )
        # save message id
        data['messages_to_del'].append(bill.message_id)

    return


"""
This function is needed to check if the good/product is available
It is impossible to pay without it
This is something like verification from the YooKassa (payment system)
"""


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    # check if the good/product is available
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True
    )

    return


async def process_payment(message: types.Message, state: FSMContext):
    # annotation
    bot_message: types.Message

    # check the type of incoming payment
    if message.successful_payment.invoice_payload == Payment.appointment.value:
        async with state.proxy() as data:
            # remove reply_markup
            await bot.edit_message_reply_markup(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                reply_markup=None
            )
            # send final instruction
            bot_message = await bot.send_message(
                chat_id=data['user_uid'],
                text=Payment.successful_payment.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.main_menu.value)
            )
            # save message id
            data['last_msg_id'] = bot_message.message_id
            # update request message
            data['request_message'] += f'\n\n{Payment.transaction_code.value}' \
                                       f'{message.successful_payment.provider_payment_charge_id}\n' \
                                       f'{Payment.transaction_sum.value}{data["price"]} ₽'
            # inform administrators that consultation is paid
            await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=data['request_msg_id'],
                text=data['request_message'],
                parse_mode='HTML'
            )
            # add new appointment to the db
            await create_appointment(
                tg_uid=data['user_uid'],
                username=data['username'],
                full_name=data['name'],
                phone=data['phone'],
                consultation_type=data['consultation_type'],
                communication_type=data['communication_type'],
                user_request=data['user_request'],
                doctor_id=data['doctor_id'],
                preferable_dt=data['datetime']
            )
            # set bot to the next state
            await FSMAppointment.next()
            # generate link for video conference
            link = generate_link()
            link_message = f'{BotMessageText.video_conf_link.value}{link}'
            # send the link to the client
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=f'{Payment.successful_payment.value}\n\n\n{link_message}',
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.main_menu.value)
            )
            # update request message
            data['request_message'] += f'\n\n{link_message}'
            # attach link to the request message in administration chat
            await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=data['request_msg_id'],
                text=data['request_message'],
                parse_mode='HTML'
            )
        # exit FSM
        await state.finish()

    return


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        fill_form,
        lambda x: x.data and x.data == CallbackData.appointment_request.value,
        state='*'
    )
    dp.register_callback_query_handler(
        get_cons_type,
        lambda x: x.data and x.data in [CallbackData.choose_offline.value, CallbackData.choose_online.value],
        state=FSMAppointment.consultation_type
    )
    dp.register_callback_query_handler(
        show_prev,
        lambda x: x.data and x.data.startswith(CallbackData.prev.value),
        state=FSMAppointment.user_request
    )
    dp.register_callback_query_handler(
        show_next,
        lambda x: x.data and x.data.startswith(CallbackData.next.value),
        state=FSMAppointment.user_request
    )
    dp.register_callback_query_handler(
        get_speciality,
        lambda x: x.data and x.data.startswith(CallbackData.speciality_title.value),
        state=FSMAppointment.user_request
    )
    dp.register_message_handler(
        get_request,
        state=FSMAppointment.user_request
    )
    dp.register_callback_query_handler(
        get_request,
        lambda x: x.data and x.data.startswith(CallbackData.doctor.value),
        state=FSMAppointment.user_request
    )
    dp.register_callback_query_handler(
        get_datetime_choice,
        lambda x: x.data and x.data in [CallbackData.yes.value, CallbackData.no.value],
        state=FSMAppointment.datetime_choice
    )
    dp.register_message_handler(
        get_datetime,
        state=FSMAppointment.datetime
    )
    dp.register_callback_query_handler(
        get_com_type,
        lambda x: x.data and x.data in [CallbackData.choose_call.value, CallbackData.choose_chat.value],
        state=FSMAppointment.communication_type
    )
    dp.register_message_handler(
        get_phone,
        state=FSMAppointment.phone,
        content_types=[types.ContentType.CONTACT, types.ContentType.TEXT]
    )
    dp.register_message_handler(
        get_name,
        state=FSMAppointment.name
    )
    dp.register_callback_query_handler(
        start_payment,
        lambda x: x.data and x.data == CallbackData.initialize_payment.value,
        state=FSMAppointment.payment
    )
    dp.register_pre_checkout_query_handler(
        process_pre_checkout_query,
        state=FSMAppointment.payment
    )
    dp.register_message_handler(
        process_payment,
        content_types=types.ContentType.SUCCESSFUL_PAYMENT,
        state=FSMAppointment.payment
    )

    return
