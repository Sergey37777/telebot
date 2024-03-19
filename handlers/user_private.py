from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from filters.ChatTypeFilter import ChatTypeFilter


user_router = Router()
user_router.message.filter(ChatTypeFilter(['private']))


@user_router.message(CommandStart())
async def menu(message: Message):
    await message.reply(f'Hello {message.from_user.full_name}')
