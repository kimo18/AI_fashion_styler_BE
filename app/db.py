from dotenv import load_dotenv
import os
from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table , Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship,Mapped
from fastapi_users.db import SQLAlchemyBaseUserTableUUID,SQLAlchemyUserDatabase,SQLAlchemyBaseOAuthAccountTableUUID

from fastapi import Depends
from sqlalchemy import Enum
from ENUMS.Clothes import Season ,Size

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://fastapi_user:123456@localhost:5432/fastapi_db")

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
    posts: Mapped[list["Posts"]] = relationship(
        "Posts",
        back_populates="user",
        lazy="selectin"     # <-- BEST OPTION
    )
    images: Mapped[list["UserImages"]] = relationship(
        "UserImages",
        back_populates="user",
        lazy="selectin"     # <-- BEST OPTION
    )



class UserImages(Base):
    __tablename__ = "UserImages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    url = Column(String, nullable=False)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="images")


####### Association Table between PostImage and Clothes ###########
postimage_clothes = Table(
    "PostImageClothes",
    Base.metadata,
    Column("post_image_id", UUID(as_uuid=True), ForeignKey("PostImages.id"), primary_key=True),
    Column("clothes_id", UUID(as_uuid=True), ForeignKey("Clothes.id"), primary_key=True)
)



###############Clothes Model####################

class Clothes(Base):
    __tablename__ = "Clothes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", back_populates="clothes")
    name = Column(String, index=True)
    in_closet = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    type = Column(String,nullable=True)
    color = Column(String,nullable=True)
    brand = Column(String, nullable=True)
    size = Column(Enum(Size),nullable=True)
    season = Column(Enum(Season), nullable=False)
    image_url = Column(String)
    description = Column(String, nullable=False)
    post_images = relationship("PostImages", secondary = postimage_clothes, back_populates="clothes",lazy="selectin")


###############Posts and PostImage Models####################
class Posts(Base):
    __tablename__ = "Posts"

    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pending = Column(Boolean, default=True)
    user = relationship("User",back_populates="posts")
    images: Mapped[list["PostImages"]] = relationship(
        "PostImages",
        back_populates="post",
        lazy="selectin",     # <-- BEST OPTION
        cascade="all, delete-orphan"
    )

class PostImages(Base):
    __tablename__ = "PostImages"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("Posts.id"),nullable=False)
    url = Column(String, nullable=False)

    # Back reference
    post = relationship("Posts", back_populates="images") 
    clothes: Mapped["Clothes"] = relationship(
        "Clothes",
        secondary=postimage_clothes,
        back_populates="post_images",
        lazy="selectin"     # <-- BEST OPTION
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