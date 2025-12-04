from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status , Body ,Form
from typing import Annotated , List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.schemas.schema import UserRead ,ClothCreate
from app.user import current_active_user
from app.db import create_db_tables, get_async_session
import uuid
from app.db import Clothes
from app.db import User
import redis as redis
from app.redis import get_user_pending_uploads
from services.Strategies.uploadstratgies import UploadStrategy,generate_supabase_signed_url
from services.registry import UPLOAD_STRATEGIES

router = APIRouter()

# Supabase client setup




class ClothUploadStrategy(UploadStrategy):
    key_name = "clothes_uploads"

    async def validate(self, uploads_req):
        if len(uploads_req.images) != 1:
            raise HTTPException(
                status_code=400,
                detail={"error": "Please provide exactly one image for cloth upload."}
            )

    async def process(self, uploads_req, user, r):
        urls = {}
        for i, img in enumerate(uploads_req.images):
            unique_filename = f"{uuid.uuid4()}_{img.file_name}"
            storage_path, signed_url = generate_supabase_signed_url(unique_filename)

            await r.hset(f"{user.id}_{self.key_name}", unique_filename, storage_path)
            await r.expire(f"{user.id}_{self.key_name}", 300)

            urls[str(i)] = signed_url
        return urls

UPLOAD_STRATEGIES["clothes"] = ClothUploadStrategy()




@router.post("/upload/")
async def upload_fit(
    data:ClothCreate,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    r: redis.Redis=Depends(get_user_pending_uploads)
):
     
    # 2. Save record in database
    try:
        pending_uploads = await r.hgetall(f"{user.id}_clothes_uploads")
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

        # Clear pending uploads from Redis
        await r.delete(f"{user.id}_clothes_uploads")

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

