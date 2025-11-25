from fastapi import FastAPI, UploadFile, File
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.user import fastapi_users, auth_backend,current_active_user, google_oauth_client
from app.schema import UserRead, UserCreate, UserUpdate
from app.db import create_db_tables, get_async_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, Request

load_dotenv()

# Load Secrets from .env
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_ANON") 
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


BUCKET = "FAShion"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await create_db_tables()
    yield
    # Shutdown code


app = FastAPI(lifespan=lifespan)

# --- CORS CONFIG ---
origins = [
    "http://localhost:8081",      # React local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allowed frontend domains
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])  
app.include_router(
    fastapi_users.get_register_router(UserRead,UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

#Google OAuth2 Routes

app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, "SECRET", redirect_url=GOOGLE_REDIRECT_URI),
    prefix="/auth/google",
    tags=["auth"],
)

from app.routes import clothes
app.include_router(clothes.router, prefix="/clothes", tags=["clothes"])



       
        
