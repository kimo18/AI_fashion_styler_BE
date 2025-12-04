from fastapi import HTTPException
from app.supabase import SUPABASE_URL, SUPABASE_KEY, BUCKET

import requests



class UploadStrategy:
    key_name: str

    async def validate(self, uploads_req):
        raise NotImplementedError

    async def process(self, uploads_req, user, redis_client):
        raise NotImplementedError





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