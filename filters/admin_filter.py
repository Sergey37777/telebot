from typing import List
from aiogram.types import Message
from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot


class AdminFilter(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: Message, bot: Bot):
        return message.from_user.id in bot.my_admins_list


