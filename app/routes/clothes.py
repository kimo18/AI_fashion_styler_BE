from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.schema import UserRead
from app.user import current_active_user
from app.db import create_db_tables, get_async_session
from supabase import create_client, Client
import uuid
from app.schema import ClothCreate
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
    closet_schema: ClothCreate,
    file: UploadFile = File(...),
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Upload file to Supabase
    try:
        contents = await file.read()
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        supabase_res = supabase.storage.from_(BUCKET).upload(
            unique_filename,
            contents,
            file_options={"cache-control": "3600", "upsert": "true"}
        )

        # Supabase returns error as dict sometimes, catch that:
        if hasattr(supabase_res, "error") and supabase_res.error:
            raise Exception(supabase_res.error)

        public_url = supabase.storage.from_(BUCKET).get_public_url(file.filename)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Supabase Upload Error: {str(e)}"}
        )

    # 2. Save record in database
    try:

        new_fit = Clothes(
            user_id=user.id,
            name=ClosetRead.name,
            type=ClosetRead.type,
            color=ClosetRead.color,
            brand=ClosetRead.brand,
            size=ClosetRead.size,
            season=ClosetRead.season,
            image_url=public_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_fit)
        await session.commit()
        await session.refresh(new_fit)

        return {"status": "success", "clothes_id": new_fit.id}

    except Exception as e:
        supabase.storage.from_(BUCKET).remove([unique_filename])
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
