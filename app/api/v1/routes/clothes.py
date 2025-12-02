from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status , Body ,Form
from typing import Annotated , List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.schemas.schema import UserRead ,ClothCreate
from app.user import current_active_user
from app.db import create_db_tables, get_async_session
from supabase import create_client, Client
import uuid
from app.db import Clothes
from app.db import User


router = APIRouter()

# Supabase client setup
from dotenv import load_dotenv
import os
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON")
BUCKET = "FAShion"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)






@router.post("/upload/")
async def upload_fit(
    data:ClothCreate = Form(..., media_type="multipart/form-data"),
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
     
    # 2. Save record in database
    try:

        new_fit = Clothes(
            user_id=user.id,
            name=data.name,
            type=data.type,
            color=data.color,
            brand=data.brand,
            size=data.size,
            season=data.season,
            image_url=data.image_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_fit)
        await session.commit()
        await session.refresh(new_fit)

        return {"status": "success", "clothes_id": new_fit.id}

    except Exception as e:
        # supabase.storage.from_(BUCKET).remove([unique_filename])
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Database Error: {str(e)}"}
        )


@router.get("")
async def list_clothes(
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        result = await session.get(User, user.id)
        clothes = result.clothes

        return {"status": "success", "clothes": clothes}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Database Error: {str(e)}"}
        )
