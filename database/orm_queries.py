from typing import Dict
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import Product, User, Category, Banner, Cart


async def orm_add_product(session: AsyncSession, data: Dict):
    obj = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        image=data['image'],
        user_id=data['user_id'],
        category_id=data['category_id']
    )
    session.add(obj)
    await session.commit()


async def orm_add_category(session: AsyncSession, data: Dict):
    obj = Category(
        name=data['name']
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id: int | None = None):
    if category_id is None:
        query = select(Product)
        result = await session.execute(query)
        return result.scalars().all()
    query = select(Product).where(Product.category_id == category_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_admins(session: AsyncSession):
    stmt = select(User)
    users = await session.execute(stmt)
    users = users.scalars().all()
    admins = []
    for user in users:
        admins.append(user.user_id)
    return admins


async def orm_get_categories(session: AsyncSession):
    stmt = select(Category)
    categories = await session.execute(stmt)
    categories = categories.scalars().all()
    return categories


async def orm_delete_product(session: AsyncSession, product_id: int):
    stmt = select(Product).where(Product.id == product_id)
    product = await session.execute(stmt)
    product = product.scalars().first()
    await session.delete(product)
    await session.commit()


async def orm_get_product(session: AsyncSession, product_id: int):
    stmt = select(Product).where(Product.id == product_id)
    product = await session.execute(stmt)
    product = product.scalars().first()
    return product


async def org_update_product(session: AsyncSession, product_id: int, data: Dict):
    stmt = select(Product).where(Product.id == product_id)
    product = await session.execute(stmt)
    product = product.scalars().first()
    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    product.image = data['image']
    product.category_id = data['category_id']
    await session.commit()


async def orm_add_banner(session: AsyncSession, data: Dict):
    obj = Banner(
        image=data['image'],
        user_id=data['user_id'],
        name=data['name'],
        description=data['description']
    )
    session.add(obj)
    await session.commit()


async def orm_get_info_pages(session: AsyncSession):
    stmt = select(Banner)
    result = await session.execute(stmt)
    return result.scalars().all()


async def orm_get_banner(session: AsyncSession, menu_name: str):
    stmt = select(Banner).where(Banner.name == menu_name)
    result = await session.execute(stmt)
    return result.scalars().first()


async def orm_get_banner_by_id(session: AsyncSession, id: int):
    stmt = select(Banner).where(Banner.id == id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def orm_get_banners(session: AsyncSession):
    stmt = select(Banner)
    result = await session.execute(stmt)
    return result.scalars().all()

async def orm_update_banner(session: AsyncSession, banner_id: int, data: Dict):
    stmt = update(Banner).where(Banner.id == banner_id).values(**data).returning()
    await session.execute(stmt)
    await session.commit()


async def orm_delete_banner(session: AsyncSession, banner_id: int):
    stmt = delete(Banner).where(Banner.id == banner_id)
    await session.execute(stmt)
    await session.commit()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    stmt = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(stmt)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(stmt)
    cart = cart.scalars().first()
    if cart.quantity == 1:
        await orm_delete_from_cart(session, user_id, product_id)
        return False
    cart.quantity -= 1
    await session.commit()
    return True


async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(stmt)
    cart = cart.scalars().first()
    if cart:
        cart.quantity += 1
        await session.commit()
        return
    cart = Cart(user_id=user_id, product_id=product_id, quantity=1)
    session.add(cart)
    await session.commit()


async def orm_get_user_carts(session: AsyncSession, user_id: int):
    stmt = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    carts = await session.execute(stmt)
    carts = carts.scalars().all()
    return carts