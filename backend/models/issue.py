from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base
import enum


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Status(str, enum.Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)

    severity = Column(Enum(Severity), default=Severity.LOW, nullable=False)
    status = Column(Enum(Status), default=Status.OPEN, nullable=False)

    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="issues_reported")

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
