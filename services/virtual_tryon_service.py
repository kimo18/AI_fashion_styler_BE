import uuid
from app.supabase import supabase, BUCKET
import asyncio

async def process_virtual_tryon(user_image_url: str, clothes_images_urls: list[dict]):

    #validate the post images, if exists and if they follow the guidelines
    
    # get userimage from supabase
    response = supabase.storage.from_(BUCKET).download(f"{user_image_url}")
    if response.status_code != 200:
        print(f"Failed to download user image {user_image_url} from Supabase.")
        return

    for cloth in clothes_images_urls:
        print(f"Processing virtual tryon for user image: {user_image_url} with cloth: {cloth['id']}")
        # Simulate processing time
        # get the image from supabase
        response = supabase.storage.from_(BUCKET).download(cloth['image_url'])
        if response.status_code != 200:
            print(f"Failed to download cloth image {cloth['id']} from Supabase.")
            return
        await asyncio.sleep(5)
