from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status , Body ,Form ,BackgroundTasks
from typing import Annotated , List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.schemas.schema import UserRead ,PostSchema
from app.user import current_active_user
from app.db import  get_async_session ,Posts,PostImages
from supabase import create_client, Client
import asyncio 
import uuid
import redis as redis
from app.redis import get_user_pending_uploads
router = APIRouter()

# Supabase client setup
from dotenv import load_dotenv
import os
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON")
BUCKET = "FAShion"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



async def process_clothes_ai(user_id: str, post_id: int , r):
    pending_uploads = await r.hgetall(f"{user_id}")
    print(pending_uploads)

    # Your long-running AI code
    # Example:
    await asyncio.sleep(10)
    print(f"Processing clothes AI for image: {user_id}")


@router.post("/upload/")
async def upload_fit(
    data: PostSchema,
    background_tasks: BackgroundTasks,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    r: redis.Redis=Depends(get_user_pending_uploads)
    
):
    
    try:
        new_post = Posts(
            user_id=user.id,
            description=data.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_post)
        await session.flush()
        await session.commit()
    

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")  


    background_tasks.add_task(
            process_clothes_ai,
            user_id=user.id,
            post_id=new_post.id,
            r=r
        )
  
    

    return {"status": status.HTTP_201_CREATED, "post_id": new_post.id}

