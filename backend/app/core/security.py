from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import asyncio
from functools import partial
from jose import jwt, JWTError
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

# Semaphore caps concurrent bcrypt ops — prevents thread pool saturation
# under heavy login load (bcrypt ~200ms CPU each, default pool = cpu_count+4)
_BCRYPT_SEM = asyncio.Semaphore(20)

async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Non-blocking bcrypt verify — runs in a thread pool so the event loop stays free."""
    async with _BCRYPT_SEM:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, verify_password, plain_password, hashed_password)

async def get_password_hash_async(password: str) -> str:
    """Non-blocking bcrypt hash — runs in a thread pool so the event loop stays free."""
    async with _BCRYPT_SEM:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_password_hash, password)

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, int]) -> str:
    """Create a new refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
