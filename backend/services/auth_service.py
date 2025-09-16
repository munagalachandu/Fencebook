from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from database import get_database
from models.auth import User, UserCreate
from bson import ObjectId

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(username: str, password: str) -> Optional[User]:
    db = get_database()
    user_doc = await db.users.find_one({"username": username})
    if not user_doc:
        return None
    if not verify_password(password, user_doc["hashed_password"]):
        return None
    return User(**user_doc)

async def create_user(user: UserCreate) -> User:
    db = get_database()
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "hashed_password": hashed_password,
        "role": user.role,
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return User(**user_doc)

async def get_user_by_username(username: str) -> Optional[User]:
    db = get_database()
    user_doc = await db.users.find_one({"username": username})
    if user_doc:
        return User(**user_doc)
    return None
