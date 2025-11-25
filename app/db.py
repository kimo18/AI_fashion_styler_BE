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
from sqlalchemy import Enum
from ENUMS.Clothes import Season ,Size

load_dotenv()
DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://fastapi_user:123456@localhost:5432/fastapi_db")

class Base(DeclarativeBase):
    pass

###############Users and OAuthAccount Models####################

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID,Base):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    clothes: Mapped[list["Clothes"]] = relationship(
        "Clothes",
        back_populates="user",
        lazy="selectin"     # <-- BEST OPTION
    )

###############Clothes Model####################

class Clothes(Base):
    __tablename__ = "closets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", back_populates="clothes")
    name = Column(String, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    type = Column(String,nullable=True)
    color = Column(String,nullable=True)
    brand = Column(String, nullable=True)
    size = Column(Enum(Size),nullable=True)
    season = Column(Enum(Season), nullable=False)
    image_url = Column(String)   


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