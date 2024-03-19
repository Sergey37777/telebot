from typing import List

from aiogram import F
from aiogram.types import Message
from aiogram.filters import Filter


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: List[str]):
        self.chat_types = chat_types

    async def __call__(self, message: Message):
        return message.chat.type in self.chat_types
