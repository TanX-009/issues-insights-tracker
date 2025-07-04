from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from monitoring.metrics import ISSUES_CREATED, REQUEST_TIME
from db import get_db
from models.issue import Issue, Severity
from models.user import UserRole
from dependencies import get_current_user, require_role
from schemas.issue import IssueUpdate, IssueOut
import os
import shutil
from typing import List
from core.logging import logger

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=IssueOut)
@REQUEST_TIME.time()
def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    severity: Severity = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_role(["REPORTER", "MAINTAINER", "ADMIN"])),
):
    file_path = None
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    issue = Issue(
        title=title,
        description=description,
        severity=severity,
        file_path=file_path,
        reporter_id=user.id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    logger.info(
        {
            "event": "issue_created",
            "user_id": user.id,
            "issue_id": issue.id,
            "severity": severity.value,
            "file_uploaded": bool(file),
        }
    )
    ISSUES_CREATED.inc()

    return issue


@router.get("/", response_model=List[IssueOut])
def list_issues(db: Session = Depends(get_db), user=Depends(get_current_user)):
    logger.info(
        {"event": "issue_list_requested", "user_id": user.id, "role": user.role.value}
    )

    if user.role.value == UserRole.REPORTER.value:
        return db.query(Issue).filter(Issue.reporter_id == user.id).all()
    return db.query(Issue).all()


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(
    issue_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    issue = db.query(Issue).get(issue_id)
    if not issue:
        logger.warning(
            {"event": "issue_not_found", "issue_id": issue_id, "user_id": user.id}
        )
        raise HTTPException(404)

    if user.role.value == UserRole.REPORTER.value and issue.reporter_id != user.id:
        logger.warning(
            {
                "event": "unauthorized_issue_access",
                "issue_id": issue_id,
                "user_id": user.id,
            }
        )
        raise HTTPException(403)

    logger.info({"event": "issue_fetched", "issue_id": issue.id, "user_id": user.id})

    return issue


@router.put("/{issue_id}", response_model=IssueOut)
def update_issue(
    issue_id: int,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(["MAINTAINER", "ADMIN"])),
):
    issue = db.query(Issue).get(issue_id)
    if not issue:
        logger.warning(
            {
                "event": "issue_update_failed_not_found",
                "issue_id": issue_id,
                "user_id": user.id,
            }
        )
        raise HTTPException(404)

    if payload.status:
        issue.status = payload.status
    if payload.severity:
        issue.severity = payload.severity

    db.commit()
    db.refresh(issue)

    logger.info(
        {
            "event": "issue_updated",
            "issue_id": issue.id,
            "updated_fields": payload.model_dump(exclude_unset=True),
            "user_id": user.id,
        }
    )

    return issue


@router.delete("/{issue_id}")
def delete_issue(
    issue_id: int, db: Session = Depends(get_db), user=Depends(require_role(["ADMIN"]))
):
    issue = db.query(Issue).get(issue_id)
    if not issue:
        logger.warning(
            {
                "event": "issue_delete_failed_not_found",
                "issue_id": issue_id,
                "user_id": user.id,
            }
        )
        raise HTTPException(404)

    db.delete(issue)
    db.commit()

    logger.info({"event": "issue_deleted", "issue_id": issue_id, "user_id": user.id})

    return {"detail": "Deleted"}
