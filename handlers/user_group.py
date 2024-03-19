from aiogram import Router, F
from aiogram.types import Message
from filters.ChatTypeFilter import ChatTypeFilter


group_router = Router()
group_router.message.filter(ChatTypeFilter(['group']))


@group_router.message()
async def group_message(message: Message):
    await message.reply(message.chat.type)
