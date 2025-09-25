import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str: return pwd_context.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd_context.verify(p, h)

class TokenData(BaseModel):
    sub: str
    role: str
    exp: int

def create_access_token(*, subject: str, role: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "role": role, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> Optional[TokenData]:
    try:
        return TokenData(**jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG]))
    except JWTError:
        return None
