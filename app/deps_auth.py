from typing import Optional, Annotated, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.security import decode_token
from app.db.models import User
from app.db.session import get_session  # your existing session dep

# Show proper login endpoint in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_session),
) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token_data = decode_token(creds.credentials)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.scalar(select(User).where(User.email == token_data.sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_role(*allowed: str) -> Callable[[User], User]:
    def _dep(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _dep
