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






@router.post("/upload/")
async def upload_fit(
    data:ClothCreate,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    r: redis.Redis=Depends(get_user_pending_uploads)
):
     
    # 2. Save record in database
    try:
        pending_uploads = await r.hgetall(f"{user.id}")
        #check if pending is only 1 size
        if len(pending_uploads) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Please upload exactly one image for the cloth."}
            )
        #get the only image url
        image_url = list(pending_uploads.values())[0]
        print(image_url)

        new_fit = Clothes(
            user_id=user.id,
            name=data.name,
            type=data.type,
            color=data.color,
            brand=data.brand,
            size=data.size,
            season=data.season,
            image_url=image_url,
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
@router.delete("/{cloth_id}")
async def delete_cloth(
    cloth_id: uuid.UUID,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        cloth = await session.get(Clothes, cloth_id)

        if not cloth or cloth.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Cloth not found."}
            )

        await session.delete(cloth)
        await session.commit()

        return {"status": "success", "message": "Cloth deleted successfully."}

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Database Error: {str(e)}"}
        )

