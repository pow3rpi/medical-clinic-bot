from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.enums import CallbackData, CacheKeys
from src.schedule.tasks.health_check import check_parser
from src.schedule.tasks.statistic import send_statistic
from src.utils.cache import update_cache

# create scheduler with specified timezone
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


def initialize_scheduler() -> None:
    # add daily job (updating cache)
    scheduler.add_job(
        func=update_cache,
        trigger='interval',
        hours=24,
        start_date=datetime.now(),
        args=[el.value for el in CacheKeys]
    )
    # add daily job (parser health check)
    scheduler.add_job(
        func=check_parser,
        trigger='cron',
        day_of_week='0-6',
        hour='5',
        minute='1',
        start_date=datetime.now()
    )
    # add weekly job (statistic)
    scheduler.add_job(
        func=send_statistic,
        trigger='cron',
        day_of_week='0',
        hour='0',
        minute='2',
        start_date=datetime.now(),
        kwargs={'period_type': CallbackData.week.value}
    )
    # add monthly job (statistic)
    scheduler.add_job(
        func=send_statistic,
        trigger='cron',
        day='1',
        hour='0',
        minute='3',
        start_date=datetime.now(),
        kwargs={'period_type': CallbackData.month.value}
    )
    # add quarterly job (statistic)
    scheduler.add_job(
        func=send_statistic,
        trigger='cron',
        month='1,4,7,10',
        day='1',
        hour='0',
        minute='4',
        start_date=datetime.now(),
        kwargs={'period_type': CallbackData.quarter.value}
    )
    # add annually job (statistic)
    scheduler.add_job(
        func=send_statistic,
        trigger='cron',
        month='1',
        day='1',
        hour='0',
        minute='5',
        start_date=datetime.now(),
        kwargs={'period_type': CallbackData.year.value}
    )
    # start scheduler
    scheduler.start()

    return
