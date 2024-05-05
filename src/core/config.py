from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import asyncio

from .secrets import DB_HOST, REDIS_PORT, TOKEN

loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN)

storage = RedisStorage2(
    host=DB_HOST,
    port=REDIS_PORT,
    pool_size=1000
)

dp = Dispatcher(
    bot=bot,
    storage=storage,
    loop=loop
)
