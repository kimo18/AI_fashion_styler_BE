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
    is_cloth: bool | None 
    file: Annotated[UploadFile, File()] = File(...)
    class Config:
        orm_mode = True


# PostImage Schema
class PostImageSchema(BaseModel):
    file: Annotated[UploadFile, File()] = File(...)
    type: str 
    clothes: List[ClothCreate] 
    class Config:
        orm_mode = True

# Post Schema



class PostClothesMetadata(BaseModel):
    image_id: int = Field(...)

class PostImageMetadata(BaseModel):
    type: str
    name: str



class PostSchema(BaseModel):
    description: str = Field(...)
    images_metadata: List[PostImageMetadata] = Field(...)
    clothes_metadata: List[PostClothesMetadata] = Field(...)
    
