from typing import Tuple, Any

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from data.config import I18N_DOMAIN, LOCALES_DIR
from database import DBCommands


db = DBCommands()


async def get_lang(user_id):
    user = await db.get_user(user_id=user_id)
    if user:
        return user.language


class ACLMiddleware(I18nMiddleware):
    async def get_user_locate(self, action: str, args: Tuple[Any]) -> str:
        user = types.User.get_current()
        return await get_lang(user.id) or user.locate


def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
