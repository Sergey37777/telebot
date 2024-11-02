from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from filters.ChatTypeFilter import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import get_customer_keyboard, get_callback_buttons, MenuCallBack

user_router = Router()
user_router.message.filter(ChatTypeFilter(['private']))


CUSTOMER_KB = get_customer_keyboard('Каталог', 'Корзина', 'История заказов', sizes=(1, 1, 1))


@user_router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    # print(message.from_user.id)
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


"""@user_router.callback_query(F.data.startswith('some_'))
async def show_catalog(query: CallbackQuery):
    num = int(query.data.split('_')[-1])

    await query.message.edit_text(
        text=f'Нажатий: {num}',
        reply_markup=get_callback_buttons(buttons={'Нажми еще раз': f'some_{num + 1}'})
    )"""


@user_router.callback_query(MenuCallBack.filter())
async def show_catalog(query: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    # print(query.data)
    # print(callback_data)
    media, reply_markup = await get_menu_content(session,
                                                 level=callback_data.level,
                                                 menu_name=callback_data.menu_name,
                                                 category=callback_data.category,
                                                 page=callback_data.page)
    # await query.message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
    await query.message.edit_media(media, reply_markup=reply_markup)
    await query.answer()
