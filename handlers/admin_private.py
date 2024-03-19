from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from filters.ChatTypeFilter import ChatTypeFilter

admin_router = Router()


admin_router.message.filter(ChatTypeFilter(['private']))


@admin_router.message(Command('menu'))
async def show_menu(message: Message):
    await message.reply(message.chat.type)