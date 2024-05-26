from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from database.models import Base
engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    """async with async_session() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)"""


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)