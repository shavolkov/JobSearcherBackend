from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.db.models import Job
from app.db.models import User
from app.deps_auth import get_current_user



router = APIRouter()

@router.get("/")
def list_jobs(
     db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    # simple read to prove the session works; returns empty until we migrate & insert
    print("VARIFIED USER " + User.__name__)
    return db.query(Job).limit(50).all()

@router.post("/")
def create_job(title: str, 
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),):
    # simple read to prove the session works; returns empty until we migrate & insert
    print("CREATED JOB")
    job = Job(title=title)
    db.add(job)
    db.commit()
    db.refresh(job)  # refresh to get id/posted_at
    return job
