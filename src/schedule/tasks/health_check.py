import validators

from src.core.config import bot
from src.core.enums import BotMessageText
from src.core.secrets import CHAT_ID
from src.parsers import generate_link


async def check_parser() -> None:
    try:
        link: str = generate_link()
        print('Successful parser health check: ', validators.url(link))
    except:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=BotMessageText.html_page_layout_changed.value,
            parse_mode='HTML'
        )

    return
