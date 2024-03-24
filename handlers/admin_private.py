from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter, or_f
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_queries import orm_add_product
from filters.ChatTypeFilter import ChatTypeFilter
from filters.admin_filter import AdminFilter
from kbds.reply import get_admin_keyboard

admin_router = Router()


admin_router.message.filter(ChatTypeFilter(['private']), AdminFilter())


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()


ADMIN_KB = get_admin_keyboard('Добавить товар',
                              'Изменить товар',
                              'Удалить товар',
                              'Посмотреть товары',
                              requests_contact=None,
                              sizes=(2, 1, 1))


@admin_router.message(Command('menu'))
async def show_menu(message: Message):
    await message.reply('Вот меню', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), or_f(Command('cancel'), F.text == 'отмена'))
async def add_product_cancel(message: Message, state: FSMContext):
    await message.answer('Вы отменили добавление товара', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(StateFilter('*'), F.text == 'Добавить товар')
async def add_product(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer('Введите название товара', reply_markup=ReplyKeyboardRemove())


@admin_router.message(StateFilter(AddProduct.name))
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer('Введите описание товара')


@admin_router.message(StateFilter(AddProduct.description))
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer('Введите цену товара')


@admin_router.message(StateFilter(AddProduct.price))
async def add_product_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddProduct.image)
    await message.answer('Отправьте фото товара')


@admin_router.message(StateFilter(AddProduct.image), F.photo)
async def add_product_image(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    data['user_id'] = message.from_user.id
    await orm_add_product(session, data)
    await message.answer(f'Товар {data["name"]} добавлен в базу данных', reply_markup=ADMIN_KB)
    await state.clear()
