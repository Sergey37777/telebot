from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, StateFilter, or_f
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_queries import orm_add_product, orm_add_category, orm_get_products, orm_get_categories
from filters.ChatTypeFilter import ChatTypeFilter
from filters.admin_filter import AdminFilter
from kbds.reply import get_admin_keyboard
from kbds.inline import get_callback_buttons, show_categories

admin_router = Router()


admin_router.message.filter(ChatTypeFilter(['private']), AdminFilter())


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category_id = State()
    image = State()


class AddCategory(StatesGroup):
    name = State()


ADMIN_KB = get_admin_keyboard('Добавить товар',
                              'Изменить товар',
                              'Добавить категорию',
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
async def add_product_price(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(price=message.text)
    await state.set_state(AddProduct.category_id)
    cats = await orm_get_categories(session)
    await message.answer('Выберите категорию',
                         reply_markup=show_categories(cats))


@admin_router.callback_query(StateFilter(AddProduct.category_id), F.data.startswith('category_'))
async def add_product_category(query: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = query.data.split('_')
    cat = int(data[-1])
    print(f'Category: {cat}')
    await state.update_data(category_id=cat)
    await state.set_state(AddProduct.image)
    await query.message.answer('Загрузите фото товара')


@admin_router.message(StateFilter(AddProduct.image), F.photo)
async def add_product_image(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    data['user_id'] = message.from_user.id
    print(data)
    await orm_add_product(session, data)
    await message.answer(f'Товар {data["name"]} добавлен в базу данных', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(F.text == 'Добавить категорию')
async def add_category(message: Message, state: FSMContext):
    await state.set_state(AddCategory.name)
    await message.answer('Введите название категории', reply_markup=ReplyKeyboardRemove())


@admin_router.message(StateFilter(AddCategory.name))
async def add_category_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await orm_add_category(session, data)
    await message.answer(f'Категория {message.text} добавлена', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(F.text == 'Посмотреть товары')
async def show_products(message: Message, session: AsyncSession):
    products = await orm_get_products(session)
    if products:
        for product in products:
            await message.answer(f'{product.name} - {product.price}',
                                 reply_markup=get_callback_buttons('Изменить', 'Удалить',
                                                                   product_id=str(product.id)))
    else:
        await message.answer('Товаров нет')
    await message.answer('Вот меню', reply_markup=ADMIN_KB)


@admin_router.callback_query(F.data.startswith('удалить_'))
async def delete_callback(query: CallbackQuery):
    return query.data
