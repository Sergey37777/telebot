from typing import List, Tuple, Dict, Union
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder
from database.models import Category


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


class AdminCallBack(CallbackData, prefix="admin"):
    action: str
    product_id: int | None = None
    category_id: int | None = None
    banner_id: Union[int, None] = None
    info_page_id: int | None = None


def get_callback_buttons(*, buttons: Dict[str, str], sizes: Tuple[int, ...] = (2, )) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, value in buttons.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=value))
    return builder.adjust(*sizes).as_markup()


def show_categories(categories: List[Category]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(InlineKeyboardButton(text=cat.name, callback_data=f'category_{cat.id}'))
    return builder.as_markup()


def get_customer_keyboard(*buttons: str, sizes: Tuple[int, ...]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))
    builder.adjust(*sizes)
    return builder.as_markup()


def get_user_main_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                                      callback_data=MenuCallBack(level=3, menu_name='cart').pack()))

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1, menu_name=c.name,
                                                                     category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(
        *,
        level: int,
        category: int,
        page: int,
        pagination_btns: dict,
        product_id: int,
        sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                                      callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    keyboard.add(InlineKeyboardButton(text='Купить 💵',
                                      callback_data=MenuCallBack(level=level, menu_name='add_to_cart',
                                                                 product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()
