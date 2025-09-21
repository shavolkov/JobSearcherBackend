from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine (sync) with pre_ping so broken connections are recycled
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# 2.0 style sessionmaker
print("HERE IS THE API SIDE" + settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# FastAPI dependency: one session per request
def get_session():
    db = SessionLocal()
    try:
        print("GOT SESSION")
        yield db
    finally:
        db.close()
