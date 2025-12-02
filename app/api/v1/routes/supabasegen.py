from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status , Body ,Form
from typing import Annotated , List
from sqlalchemy.ext.asyncio import AsyncSession
from app.user import current_active_user
from app.db import create_db_tables, get_async_session
from supabase import create_client, Client
import uuid

from app.api.v1.schemas.schema import UserRead
from app.redis import get_user_pending_uploads
import redis.asyncio as redis
import requests
from pydantic import BaseModel
router = APIRouter()

# Supabase client setup
from dotenv import load_dotenv
import os
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON")
BUCKET = "FAShion"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)







class PostImage(BaseModel):
    file_name: str

class PostRequest(BaseModel):
    images: List[PostImage]



def generate_supabase_signed_url(file_name: str):
    url = f"{SUPABASE_URL}/storage/v1/object/upload/sign/{BUCKET}/{file_name}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json={})

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return url ,response.json()


@router.post("/generate-upload-urls/")
async def get_upload_urls(post: PostRequest , user: UserRead = Depends(current_active_user) , r: redis.Redis=Depends(get_user_pending_uploads)):
    urls = {}
    image_count = 0
    for img in post.images:
        print("hi")
        unique_filename = f"{uuid.uuid4()}_{img.file_name}"
        storage_path,urls[f"{image_count}"] = generate_supabase_signed_url(unique_filename)
        key = f"{user.id}"
        await r.hset(f"{user.id}", unique_filename, storage_path)
        await r.expire(f"{user.id}", 3600)
       
        image_count += 1
    return {"urls": urls}




