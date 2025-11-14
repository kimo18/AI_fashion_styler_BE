from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, UploadFile, File
# Replace with your actual values
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_ANON") 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)




def upload_image(file_path: str, bucket_name: str = "images"):
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(file_name, f)

    if res.status_code != 200:
        print("Upload failed:", res)
        return None

    # Get the public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    return public_url


url = upload_image(File(...))
print("Image URL:", url)
