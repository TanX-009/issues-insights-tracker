import enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .base import Base


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    MAINTAINER = "MAINTAINER"
    REPORTER = "REPORTER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)
    issues_reported = relationship(
        "Issue", back_populates="reporter", passive_deletes=True
    )


class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole

    class Config:
        from_attributes = True
