from typing import List, Tuple

from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard(*buttons: str, requests_contact: None | List[int], sizes: Tuple[int, ...]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for idx, text in enumerate(buttons):
        if requests_contact and idx in requests_contact:
            builder.add(KeyboardButton(text=text, request_contact=True))
        else:
            builder.add(KeyboardButton(text=text))
    builder.adjust(*sizes)
    return builder.as_markup()


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Отмена')]],
        resize_keyboard=True,
    )

