from dotenv import load_dotenv
import os
from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship,Mapped
from fastapi_users.db import SQLAlchemyBaseUserTableUUID,SQLAlchemyUserDatabase,SQLAlchemyBaseOAuthAccountTableUUID

from fastapi import Depends

load_dotenv()
DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://fastapi_user:123456@localhost:5432/fastapi_db")




class Base(DeclarativeBase):
    pass

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID,Base):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )





engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)