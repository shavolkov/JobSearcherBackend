from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas_auth import RegisterIn, LoginIn, TokenOut, UserOut
from app.security import hash_password, verify_password, create_access_token
from app.db.models import User
from app.db.session import get_session

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_session)):
    print("GOTTEN ")
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email,
                hashed_password=hash_password(payload.password),
                role=payload.role or "user")
    db.add(user); db.commit(); db.refresh(user)
    return UserOut(id=user.id, email=user.email, role=user.role)

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_session)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.email, role=user.role)
    return TokenOut(access_token=token)
