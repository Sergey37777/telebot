from aiogram import Bot, Dispatcher, types
import asyncio
import logging
import sys
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database.orm_queries import get_admins
from handlers.admin_private import admin_router
from handlers.user_group import group_router
from handlers.user_private import user_router
from common.bot_commands import private
from config import token
from database.engine import async_session as session_maker, create_db
from middlewares.db import DatabaseMiddleware

dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(group_router)
dp.include_router(user_router)
# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']


async def on_startup(bot):
    # await drop_db()
    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DatabaseMiddleware(session_pool=session_maker))
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=token, default=default)
    async with session_maker() as session:
        bot.my_admins_list = await get_admins(session)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


