from typing import Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Product, User, Category, Banner


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


async def orm_get_products(session: AsyncSession):
    query = select(Product)
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
        user_id=data['user_id']
    )
    session.add(obj)
    await session.commit()
