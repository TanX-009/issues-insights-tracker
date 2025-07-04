from pydantic import BaseModel
from enum import Enum
from typing import Optional


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
    status: Optional[Status]
    severity: Optional[Severity]


class IssueOut(IssueBase):
    id: int
    status: Status
    severity: Severity = Severity.LOW
    file_path: Optional[str]
    reporter_id: int

    class Config:
        orm_mode = True
