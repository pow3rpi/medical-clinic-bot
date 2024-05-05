from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import zip_longest
from typing import Any, Dict, List, Union, Tuple
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from src.core.config import bot
from src.core.enums import (
    CallbackData, Symbols, DateFormat, Statistic,
    ConsultationType, BotMessageText
)
from src.db.base import Base
from src.db.models import Appointment, CallBack, Feedback, User
from src.db.query import calculate_statistic
from src.keyboards import back_to_menu
from src.keyboards.navigation import check_access

timedelta: Dict[str, relativedelta] = {
    CallbackData.day.value: relativedelta(hours=24),
    CallbackData.week.value: relativedelta(days=7),
    CallbackData.month.value: relativedelta(months=1),
    CallbackData.quarter.value: relativedelta(months=3),
    CallbackData.year.value: relativedelta(years=1)
}


# define finite-state machine
class FSMStatistics(StatesGroup):
    period = State()


async def show_standard_statistics(callback_query: types.CallbackQuery):
    # annotation
    period_type: str
    end_date: datetime
    delta: relativedelta
    start_date: datetime
    start_date_prev: datetime
    stats: Dict[Base, Any]

    # check user access
    if await check_access(user_uid=callback_query.from_user.id):
        # get the period type
        period_type = callback_query.data.split(Symbols.separator.value)[1]
        # get the current time
        end_date = datetime.now()
        # calculate delta basing on period type
        delta = timedelta[period_type]
        # calculate starting dates
        start_date = end_date - delta
        start_date_prev = start_date - delta
        # calculate statistic for chosen period
        stats = await get_statistic(
            start_date=start_date,
            end_date=end_date,
            start_date_prev=start_date_prev,
            change=True
        )
        # show statistics for the specified period
        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=BotMessageText.statistic(
                n_appointment_online=stats[Appointment][ConsultationType.online.value][Statistic.statistic.value],
                n_appointment_offline=stats[Appointment][ConsultationType.offline.value][Statistic.statistic.value],
                n_callback=stats[CallBack][Statistic.statistic.value],
                n_feedback=stats[Feedback][Statistic.statistic.value],
                n_new_users=stats[User][Statistic.statistic.value],
                online_change=stats[Appointment][ConsultationType.online.value][Statistic.change.value],
                offline_change=stats[Appointment][ConsultationType.offline.value][Statistic.change.value],
                callback_change=stats[CallBack][Statistic.change.value],
                new_users_change=stats[User][Statistic.change.value],
                period_type=period_type
            ),
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.statistics.value)
        )
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.statistics.value)
        )

    return


async def show_custom_statistics(callback_query: types.CallbackQuery, state: FSMContext):
    # exit FSM (if not finished)
    await state.finish()
    # check user access
    if await check_access(user_uid=callback_query.from_user.id):
        # ask to enter the period
        await callback_query.message.edit_text(
            text=BotMessageText.ask_period.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.statistics.value)
        )
        # set the first state (enter FSM)
        await FSMStatistics.period.set()
        # save message id and user uid
        async with state.proxy() as data:
            data['last_msg_id'] = callback_query.message.message_id
            data['user_uid'] = callback_query.from_user.id
    else:
        # send warning that user doesn't have enough privileges
        await callback_query.message.edit_text(
            text=BotMessageText.lack_of_privileges.value,
            parse_mode='HTML',
            reply_markup=back_to_menu(section=CallbackData.statistics.value)
        )

    return


async def get_period(message: types.Message, state: FSMContext):
    # annotation
    period: Union[List[datetime], List[str]]
    start_date: Union[str, datetime]
    end_date: Union[str, datetime]
    stats: Dict[Base, Any]

    # get the period
    period = re.sub(r'\s+', ' ', message.text).strip().split(' ')
    try:
        # validate input
        period = [datetime.strptime(date, DateFormat.input.value) for date in period]
        # calculate period borders
        start_date = datetime.strftime(period[0 if period[0] < period[1] else 1], DateFormat.system.value)
        end_date = datetime.strftime(period[1 if period[0] < period[1] else 0], DateFormat.system.value)
        start_date = datetime.strptime(start_date, DateFormat.system.value)
        end_date = datetime.strptime(end_date, DateFormat.system.value)
    except (IndexError, ValueError):
        # delete answer
        await message.delete()
        # ask to enter the period again
        async with state.proxy() as data:
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.ask_period_again.value,
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.statistics.value)
            )
    else:
        # delete answer
        await message.delete()
        # calculate statistic for chosen period
        stats = await get_statistic(
            start_date=start_date,
            end_date=end_date
        )
        async with state.proxy() as data:
            # show statistics for the specified period
            await bot.edit_message_text(
                chat_id=data['user_uid'],
                message_id=data['last_msg_id'],
                text=BotMessageText.statistic(
                    n_appointment_online=stats[Appointment][ConsultationType.online.value][Statistic.statistic.value],
                    n_appointment_offline=stats[Appointment][ConsultationType.offline.value][Statistic.statistic.value],
                    n_callback=stats[CallBack][Statistic.statistic.value],
                    n_feedback=stats[Feedback][Statistic.statistic.value],
                    n_new_users=stats[User][Statistic.statistic.value],
                    start_date=datetime.strftime(start_date, DateFormat.output.value),
                    end_date=datetime.strftime(end_date, DateFormat.output.value)
                ),
                parse_mode='HTML',
                reply_markup=back_to_menu(section=CallbackData.statistics.value)
            )
        # exit FSM
        await state.finish()

    return


async def get_statistic(start_date: datetime, end_date: datetime, start_date_prev: Union[str, datetime] = None,
                        change: bool = False) -> Dict[Base, Any]:
    # annotation
    tables: Tuple[Base, Base, Base, Base, Base]
    cons_types: Tuple[str, str]
    result: Dict[Base, Any]
    statistic: int
    statistic_change: Union[float, int]

    # specify tables to calculate statistics (do not change the sequence)
    tables = (Appointment, Appointment, CallBack, Feedback, User)
    cons_types = (ConsultationType.online.value, ConsultationType.offline.value)
    result = {table: {} for table in set(tables)}
    for table, cons_type in zip_longest(tables, cons_types):
        # calculate statistic for chosen period
        statistic = await calculate_statistic(
            table=table,
            start_date=start_date,
            end_date=end_date,
            consultation_type=cons_type
        )
        # check table and save the result
        if table == Appointment:
            result[table][cons_type] = {Statistic.statistic.value: statistic}
        else:
            result[table][Statistic.statistic.value] = statistic
        # check if it is needed to calculate statistic change
        if change:
            # check table (we don't calculate change for Feedback)
            if table != Feedback:
                # calculate statistic change comparing with previous period
                try:
                    statistic_change = statistic / await calculate_statistic(
                        table=table,
                        start_date=start_date_prev,
                        end_date=start_date,
                        consultation_type=cons_type
                    ) * 100 - 100
                except ZeroDivisionError:
                    statistic_change = 0.0 if statistic == 0 else 100
                else:
                    statistic_change = round(statistic_change, 1) if abs(statistic_change) < 100 else int(statistic_change)
                finally:
                    # check table and save the result
                    if table == Appointment:
                        result[table][cons_type][Statistic.change.value] = statistic_change
                    else:
                        result[table][Statistic.change.value] = statistic_change

    return result


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        show_standard_statistics,
        lambda x: x.data and x.data.startswith(CallbackData.statistics.value + Symbols.separator.value),
        state='*'
    )
    dp.register_callback_query_handler(
        show_custom_statistics,
        lambda x: x.data and x.data == CallbackData.custom_statistics.value,
        state='*'
    )
    dp.register_message_handler(
        get_period,
        state=FSMStatistics.period
    )

    return
