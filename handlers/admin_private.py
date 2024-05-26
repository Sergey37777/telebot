from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, StateFilter, or_f
from aiogram.utils.formatting import Text, Bold
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_queries import orm_add_product, orm_add_category, orm_get_products, orm_get_categories, \
    orm_delete_product, orm_get_product, org_update_product, orm_add_banner, orm_get_info_pages
from filters.ChatTypeFilter import ChatTypeFilter
from filters.admin_filter import AdminFilter
from kbds.reply import get_admin_keyboard
from kbds.inline import get_callback_buttons, show_categories
from decimal import Decimal

admin_router = Router()

admin_router.message.filter(ChatTypeFilter(['private']), AdminFilter())


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category_id = State()
    image = State()

    product_for_change = None

    texts = {
        'name': 'Введите новое название или точку, что-бы пропустить',
        'description': 'Введите новое описание или точку, что-бы пропустить',
        'price': 'Введите новую цену или точку что-бы пропустить',
        'image': 'Загрузите новое фото или введите точку, что-бы пропустить'
    }


class AddCategory(StatesGroup):
    name = State()


class AddBanner(StatesGroup):
    image = State()


ADMIN_KB = get_admin_keyboard('Добавить товар',
                              'Добавить баннер',
                              'Добавить категорию',
                              'Посмотреть товары',
                              requests_contact=None,
                              sizes=(2, 1, 1))


@admin_router.message(Command('menu'))
async def show_menu(message: Message):
    await message.reply('Вот меню', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), or_f(Command('cancel'), F.text == 'отмена'))
async def add_product_cancel(message: Message, state: FSMContext):
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
        await state.clear()
        await message.answer('Вы отменили изменение товара', reply_markup=ADMIN_KB)
    else:
        await message.answer('Вы отменили добавление товара', reply_markup=ADMIN_KB)
        await state.clear()


@admin_router.message(StateFilter('*'), F.text == 'Добавить товар')
async def add_product(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer('Введите название товара', reply_markup=ReplyKeyboardRemove())


@admin_router.message(StateFilter(AddProduct.name))
async def add_product_name(message: Message, state: FSMContext):
    if AddProduct.product_for_change and message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.name)
        await state.set_state(AddProduct.description)
        await message.answer(AddProduct.texts['description'])
    else:
        await state.update_data(name=message.text)
        await state.set_state(AddProduct.description)
        await message.answer('Введите описание товара')


@admin_router.message(StateFilter(AddProduct.description))
async def add_product_description(message: Message, state: FSMContext):
    if AddProduct.product_for_change and message.text == '.':
        await state.update_data(description=AddProduct.product_for_change.description)
        await state.set_state(AddProduct.price)
        await message.answer(AddProduct.texts['price'])
    else:
        await state.update_data(description=message.text)
        await state.set_state(AddProduct.price)
        await message.answer('Введите цену товара')


@admin_router.message(StateFilter(AddProduct.price))
async def add_product_price(message: Message, state: FSMContext, session: AsyncSession):
    cats = await orm_get_categories(session)
    if AddProduct.product_for_change and message.text == '.':
        await state.update_data(price=AddProduct.product_for_change.price)
        await state.set_state(AddProduct.category_id)
        await message.answer('Выберите новую категорию',
                             reply_markup=show_categories(cats))
    else:
        await state.update_data(price=message.text)
        await state.set_state(AddProduct.category_id)
        await message.answer('Выберите категорию',
                             reply_markup=show_categories(cats))


@admin_router.callback_query(StateFilter(AddProduct.category_id), F.data.startswith('category_'))
async def add_product_category(query: CallbackQuery, state: FSMContext):
    data = query.data.split('_')
    cat = int(data[-1])
    await query.answer()
    await state.update_data(category_id=cat)
    await state.set_state(AddProduct.image)
    await query.message.answer('Загрузите фото товара')


@admin_router.message(StateFilter(AddProduct.image), or_f(F.photo, F.text == '.'))
async def add_product_image(message: Message, state: FSMContext, session: AsyncSession):
    if AddProduct.product_for_change and message.text == '.':
        await state.update_data(image=AddProduct.product_for_change.image)
        data = await state.get_data()
        data['user_id'] = message.from_user.id
        await org_update_product(session, AddProduct.product_for_change.id, data)
        AddProduct.product_for_change = None
        await message.answer('Товар изменен', reply_markup=ADMIN_KB)
    else:
        await state.update_data(image=message.photo[-1].file_id)
        data = await state.get_data()
        data['user_id'] = message.from_user.id
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
            content = Text(Bold(product.name) +
                           f'\n{product.description}\n{Decimal(product.price)}\n{product.category.name}').as_html()
            await message.answer_photo(photo=product.image, caption=content,
                                       reply_markup=get_callback_buttons(buttons={'Изменить': f'update_{product.id}',
                                                                                  'Удалить': f'delete_{product.id}'}))
    await message.answer('Товаров нет')


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_callback(query: CallbackQuery, session: AsyncSession):
    await orm_delete_product(session=session, product_id=int(query.data.split('_')[-1]))
    await query.answer('Товар удален', reply_markup=ADMIN_KB)


@admin_router.callback_query(F.data.startswith('update_'))
async def change_product_callback(query: CallbackQuery, session: AsyncSession, state: FSMContext):
    product_id = int(query.data.split('_')[-1])
    product = await orm_get_product(session, product_id)
    AddProduct.product_for_change = product
    await state.set_state(AddProduct.name)
    await query.message.answer(AddProduct.texts['name'], reply_markup=ReplyKeyboardRemove())
    await query.answer()


@admin_router.message(StateFilter('*'), F.text == 'Добавить баннер')
async def add_banner(message: Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                             \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)


@admin_router.message(StateFilter(AddBanner.image), F.photo)
async def add_banner_image(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    data['user_id'] = message.from_user.id
    await orm_add_banner(session, data)
    await state.clear()
    await message.answer('Баннер добавлен', reply_markup=ADMIN_KB)
