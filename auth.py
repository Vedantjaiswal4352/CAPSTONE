# auth.py -> Authentication and Authorization module.
import os
import logging
from datetime import datetime, timezone,timedelta
from typing import Optional, List, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("capstone_auth")

SECRET_KEY = os.getenv("SECRET_KEY","capstone_secret_key_advanced")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))

# Advanced user mgmnt with roles
user_db = {
    "user": {"password":"pass","role":"user"},
    "admin": {"password":"admin","role":"admin"}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    """Create JWT access token with optional expiration"""
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme))-> Dict:
    """Verify JWT token and return user info."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"username": username, "role": role}
    except JWTError:
        logger.error("Invalid JWT token attempt.")
        raise HTTPException(status_code=401, detail="invalid token.")

def require_admin(user: dict = Depends(get_current_user))-> dict:
    """Dependency to require admin role"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")