from fastapi import FastAPI, Request, HTTPException, UploadFile, File
import redis.asyncio as redis
import time

app = FastAPI()

# --- SETTINGS ---
MAX_IMAGES_PER_HOUR = 100
WINDOW = 3600  # 1 hour

@app.on_event("startup")
async def startup():
    app.state.redis = redis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)


# replace with real JWT user
def get_user_id(request: Request):
    return request.headers.get("x-user-id", "anonymous")


async def check_image_limit(user_id: str, images_count: int):
    r = app.state.redis
    key = f"user:{user_id}:image_count"
    
    current = await r.get(key)
    current = int(current) if current else 0

    if current + images_count > MAX_IMAGES_PER_HOUR:
        raise HTTPException(429, "Image upload limit (100 per hour) exceeded.")

    # Increase count and set expiry if new key
    if current == 0:
        await r.set(key, images_count, ex=WINDOW)
    else:
        await r.incrby(key, images_count)


@app.post("/post")
async def create_post(
    request: Request,
    images: list[UploadFile] = File(...)
):
    user_id = get_user_id(request)
    num_images = len(images)

    await check_image_limit(user_id, num_images)

    return {"message": f"Post created with {num_images} images"}
