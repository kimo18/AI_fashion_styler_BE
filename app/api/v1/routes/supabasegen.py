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
from services.registry import UPLOAD_STRATEGIES

class FileUpload(BaseModel):
    file_name: str

class UploadRequest(BaseModel):
    type: str
    images: List[FileUpload]


router = APIRouter()


@router.post("/generate-upload-urls/")
async def get_upload_urls(uploads_req: UploadRequest , user: UserRead = Depends(current_active_user) , r: redis.Redis=Depends(get_user_pending_uploads)):
    urls = {}
    if not uploads_req.images:
        raise HTTPException(status_code=400, detail={"error": "No images provided"})

    strategy = UPLOAD_STRATEGIES.get(uploads_req.type)
    if not strategy:
        raise HTTPException(status_code=400, detail={"error": "Invalid upload type"})

    await strategy.validate(uploads_req)

    urls = await strategy.process(uploads_req, user, r)

    return {"urls": urls}
 




