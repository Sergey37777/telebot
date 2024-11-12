from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession
from config import ADMIN_TOKEN
from database.orm_queries import orm_add_user, orm_add_to_cart, orm_check_user, orm_generate_admin_token, \
    orm_become_admin, get_admins
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


@user_router.message(Command('generate_admin_token'))
async def generate_admin_token(message: Message, session: AsyncSession):
    token = message.text.split()[-1]
    if token == ADMIN_TOKEN:
        await orm_generate_admin_token(session)
        await message.answer('Токен сгенерирован')


@user_router.message(Command('become_admin'))
async def become_admin(message: Message, session: AsyncSession, bot):
    token = message.text.split()[-1]
    if await orm_become_admin(session, message.from_user.id, token):
        await message.answer('Вы стали админом')
        bot.my_admins_list = await get_admins(session)
    else:
        await message.answer('Неверный токен')



"""@user_router.callback_query(F.data.startswith('some_'))
async def show_catalog(query: CallbackQuery):
    num = int(query.data.split('_')[-1])

    await query.message.edit_text(
        text=f'Нажатий: {num}',
        reply_markup=get_callback_buttons(buttons={'Нажми еще раз': f'some_{num + 1}'})
    )"""


async def add_to_cart(query: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = query.from_user
    if not await orm_check_user(session, user.id):
        await orm_add_user(session, user.id, user.first_name, user.last_name)
    await orm_add_to_cart(session, user.id, callback_data.product_id)
    await query.answer('Товар добавлен в корзину')


@user_router.callback_query(MenuCallBack.filter())
async def show_catalog(query: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    # print(query.data)
    # print(callback_data)
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(query, callback_data, session)
        return
    media, reply_markup = await get_menu_content(session,
                                                 level=callback_data.level,
                                                 menu_name=callback_data.menu_name,
                                                 category=callback_data.category,
                                                 page=callback_data.page,
                                                 product_id=callback_data.product_id,
                                                 user_id=query.from_user.id)
    # await query.message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
    await query.message.edit_media(media, reply_markup=reply_markup)
    await query.answer()
