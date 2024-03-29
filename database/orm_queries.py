from typing import Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Product, User, Category


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
