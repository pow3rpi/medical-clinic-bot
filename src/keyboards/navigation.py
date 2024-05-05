from typing import Dict, FrozenSet, List

from aiogram.types import InlineKeyboardMarkup

from src.core.enums import CallbackData, CacheKeys
from src.core.secrets import MASTER_ADMIN
from src.keyboards import (
    admin_panel_menu, main_menu_admin, main_menu_client,
    doctors_settings_menu, statistics_menu, admins_config_menu
)
from src.utils.cache import get_cache

# Admin menu navigation dictionary, basing on CallbackData
admin_nav: Dict[str, InlineKeyboardMarkup] = {
    CallbackData.main_menu.value: main_menu_admin,
    CallbackData.admin_panel.value: admin_panel_menu,
    CallbackData.statistics.value: statistics_menu,
    CallbackData.doctors_settings.value: doctors_settings_menu,
    CallbackData.admins.value: admins_config_menu
}

# Client menu navigation dictionary, basing on CallbackData
client_nav: Dict[str, InlineKeyboardMarkup] = {
    CallbackData.main_menu.value: main_menu_client
}

# pages which can be accessed only by admins
admin_pages: FrozenSet = frozenset([
    CallbackData.admin_panel.value,
    CallbackData.doctors_settings.value
])

# pages which can be accessed only by MASTER_ADMIN and high privilege admins
privilege_pages: FrozenSet = frozenset([
    CallbackData.statistics.value,
    CallbackData.admins.value
])


# check user access
async def check_access(user_uid: int) -> bool:
    priv_admins: List[int] = await get_cache(key=CacheKeys.priv_admins.value)
    if user_uid == MASTER_ADMIN or user_uid in priv_admins:
        return True
    else:
        return False
