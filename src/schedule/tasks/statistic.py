from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Any, Dict

from src.core.config import bot
from src.core.enums import BotMessageText, ConsultationType, Statistic
from src.core.secrets import CHAT_ID_STATISTIC
from src.db.base import Base
from src.db.models import Appointment, CallBack, Feedback, User
from src.handlers.admin.statistic import get_statistic, timedelta


async def send_statistic(period_type: str) -> None:
    # annotate variables
    end_date: datetime
    start_date: datetime
    start_date_prev: datetime
    delta: relativedelta
    stats: Dict[Base, Any]

    # get the current time
    end_date = datetime.now()
    # calculate delta basing on period type
    delta = timedelta[period_type]
    # calculate starting dates
    start_date = end_date - delta
    start_date_prev = start_date - delta
    # calculate statistic for the specified period
    stats = await get_statistic(
        start_date=start_date,
        end_date=end_date,
        start_date_prev=start_date_prev,
        change=True
    )
    # send statistic to the chat
    await bot.send_message(
        chat_id=CHAT_ID_STATISTIC,
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
            period_type=period_type,
            scheduler=True
        ),
        parse_mode='HTML'
    )

    return
