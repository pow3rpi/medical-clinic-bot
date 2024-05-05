from aiogram.utils import executor

from src.core.config import dp
from src.core.enums import CacheKeys
from src.handlers import registration
from src.schedule import initialize_scheduler
from src.utils.cache import cache, update_cache


async def on_startup(_) -> None:
    initialize_scheduler()
    await update_cache(*[el.value for el in CacheKeys])
    print('Bot has been successfully activated!')

    return


async def on_shutdown(_) -> None:
    cache.close()
    await dp.storage.close()

    return


if __name__ == "__main__":
    # register all handlers
    registration.register_handlers(dp)
    # start bot with config
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )

