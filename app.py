import asyncio

from aiogram import executor

from database import create_db
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # await db.create
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await create_db()
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    from admin_panel import dp
    from handlers.users.shop_handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
