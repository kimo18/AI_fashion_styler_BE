from fastapi_users import schemas
from fastapi import UploadFile
from ENUMS.Clothes import Season ,Size
from pydantic import BaseModel
import uuid


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass
class UserCreate(schemas.BaseUserCreate):
    pass
class UserUpdate(schemas.BaseUserUpdate):
    pass


class ClothCreate(BaseModel):
    name: str
    type: str | None
    color: str | None
    brand: str | None
    size: Size | None
    season: Season | None
