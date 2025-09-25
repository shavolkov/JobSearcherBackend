from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, DateTime, func, Integer
class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(120))
    remote: Mapped[bool] = mapped_column(default=False)
    posted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    link: Mapped[str | None] = mapped_column(String(512))


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)  # "user" | "admin"
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())