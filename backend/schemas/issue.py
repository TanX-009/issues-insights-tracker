from pydantic import BaseModel
from enum import Enum
from typing import Optional

from models.user import UserOut


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Status(str, Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class IssueBase(BaseModel):
    title: str
    description: str
    severity: Severity = Severity.LOW


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    severity: Optional[Severity] = None


class IssueOut(IssueBase):
    id: int
    status: Status
    severity: Severity = Severity.LOW
    file_path: Optional[str]
    reporter: UserOut

    class Config:
        from_attributes = True
