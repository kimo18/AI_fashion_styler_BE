from fastapi_users import schemas
from fastapi import UploadFile ,File ,Form 
from ENUMS.Clothes import Season ,Size
from pydantic import BaseModel , Field
from typing import List, Optional, Annotated
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
    is_cloth: bool 
    image_url: str
    # class Config:
    #     orm_mode = True


# PostImage Schema


class PostImageSchema(BaseModel):
    type: str 
    image_url: str

class PostSchema(BaseModel):
    description: str | None
    images_metadata: List[PostImageSchema]

    
