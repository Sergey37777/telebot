from typing import List

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder

from database.models import Category


def get_callback_buttons(*buttons: str, product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, button in enumerate(buttons):
        builder.add(InlineKeyboardButton(text=button, callback_data=f'{button}_{product_id}'))
    return builder.as_markup()


def show_categories(categories: List[Category]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(InlineKeyboardButton(text=cat.name, callback_data=f'category_{cat.id}'))
    return builder.as_markup()
