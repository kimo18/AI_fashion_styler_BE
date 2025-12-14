from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status , Body ,Form ,BackgroundTasks
from typing import Annotated , List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.schemas.schema import UserRead ,PostSchema
from app.user import current_active_user
from app.db import  get_async_session ,Posts,User,UserImages ,Clothes ,PostImages
from services.Strategies.uploadstratgies import UploadStrategy,generate_supabase_signed_url
import asyncio 
import uuid
import redis as redis
from app.redis import get_user_pending_uploads
from services.registry import UPLOAD_STRATEGIES
from services.virtual_tryon_service import process_virtual_tryon
from pydantic import BaseModel

router = APIRouter()


class VirtualTryOnClothes(BaseModel):
    user_image_id: List[uuid.UUID]
    clothes_image_id: List[uuid.UUID] 

class VirtualTryOnPosts(BaseModel):
    user_image_id: List[uuid.UUID]
    post_image_id: int     









@router.post("/clothes/")
async def try_clothes(
    data: VirtualTryOnClothes,
    background_tasks: BackgroundTasks,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    
):
    
    if data.user_image_id is None or len(data.user_image_id) ==0:
        raise HTTPException(
            status_code=400,
            detail={"error": "Please provide at least one user image id."}
        )
    
    try:
        for user_image_id in data.user_image_id:
            user_image = await session.get(UserImages, user_image_id)
            if not user_image or user_image.user_id != user.id:
                raise HTTPException(
                    status_code=404,
                    detail={"error": f"User image with id {user_image_id} not found."}
                )
            
            clothes_metadata = []
            for cloth_image_id in data.clothes_image_id:
                
                cloth = await session.get(Clothes, cloth_image_id)
                if cloth is None:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": f"Cloth with id {cloth_image_id} not found."}
                    )
                clothes_metadata.append({
                    "id": cloth.id,
                    "image_url": cloth.image_url,
                    "description": cloth.description,
                    "type": cloth.type
                })
            # Add background task to process virtual tryon for each user image
            result=process_virtual_tryon(user_image,clothes_metadata)
   
        return {"status": status.HTTP_202_ACCEPTED, "images_processed": len(result)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "An error occurred while validating user images."}
        )        

    


@router.post("/posts/")
async def try_post_clothes(
    data: VirtualTryOnPosts,
    background_tasks: BackgroundTasks,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    
):
    
    if data.user_image_id is None or len(data.user_image_id) ==0:
        raise HTTPException(
            status_code=400,
            detail={"error": "Please provide at least one user image id."}
        )
    
    try:
        post = await session.get(PostImages, data.post_image_id)
        if post is None or post.user_id != user.id:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Post with id {data.post_image_id} not found."}
            )
        
        for user_image_id in data.user_image_id:
            user_image = await session.get(UserImages, user_image_id)
            if not user_image or user_image.user_id != user.id:
                raise HTTPException(
                    status_code=404,
                    detail={"error": f"User image with id {user_image_id} not found."}
                )
            
            clothes_metadata = []
            for post_image in post.images:
                for cloth in post_image.clothes:
                    clothes_metadata.append({
                        "id": cloth.id,
                        "image_url": cloth.image_url,
                        "description": cloth.description,
                        "type": cloth.type
                    })
            # Add background task to process virtual tryon for each user image
            result=process_virtual_tryon(user_image,clothes_metadata)
   
        return {"status": status.HTTP_202_ACCEPTED, "images_processed": len(result)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "An error occurred while validating user images."}
        )
