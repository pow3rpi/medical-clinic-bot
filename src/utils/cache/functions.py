from typing import Any, Dict

from src.core.secrets import CACHE_TIME
from src.core.enums import CacheKeys, AdminPrivilegeType
from src.db.query import get_admins_ids, get_specialities
from .db_cache import cache

# functions which fill cache under particular keys
cache_related_funcs: Dict[str, Dict[str, Any]] = {
    CacheKeys.admins.value: {
        'func': get_admins_ids,
        'kwargs': {}
    },
    CacheKeys.specialities.value: {
        'func': get_specialities,
        'kwargs': {}
    },
    CacheKeys.priv_admins.value: {
        'func': get_admins_ids,
        'kwargs': {
            'privilege_type': AdminPrivilegeType.high.value
        }
    }
}


async def get_cache(key):
    try:
        # update cache (if empty)
        if cache.get(key=key) is None:
            cache.set(
                key=key,
                value=await cache_related_funcs[key]['func'](**cache_related_funcs[key]['kwargs']),
                expire=CACHE_TIME
            )
        return cache.get(key=key)
    except:
        # if cache doesn't work use db query
        return await cache_related_funcs[key]['func'](**cache_related_funcs[key]['kwargs']),


async def update_cache(*keys) -> None:
    for key in keys:
        cache.set(
            key=key,
            value=await cache_related_funcs[key]['func'](**cache_related_funcs[key]['kwargs']),
            expire=CACHE_TIME
        )

    return
