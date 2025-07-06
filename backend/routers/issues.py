import asyncio
from uuid import uuid4
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session, joinedload
from starlette.responses import StreamingResponse
from monitoring.metrics import ISSUES_CREATED, REQUEST_TIME
from db import get_db
from models.issue import Issue, Severity
from models.user import UserRole
from dependencies import get_current_user, require_role
from schemas.issue import IssueUpdate, IssueOut
import os
import shutil
import json
from typing import List
from core.logging import logger

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


connected_clients: List[asyncio.Queue] = []


@router.get("/events")
async def sse_subscribe():
    """
    Endpoint for clients to subscribe to Server-Sent Events (SSE).
    Clients will receive updates when new issues are created.
    """
    client_queue = asyncio.Queue()
    connected_clients.append(client_queue)
    logger.info(f"New SSE client connected. Total clients: {len(connected_clients)}")

    async def event_generator():
        try:
            while True:
                # Wait for a new message to be put into the queue
                message = await client_queue.get()
                # Format the message as an SSE event
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            # This exception is raised when the client disconnects
            logger.info("SSE client disconnected.")
        finally:
            # Ensure the client's queue is removed when they disconnect
            connected_clients.remove(client_queue)
            logger.info(f"SSE client removed. Total clients: {len(connected_clients)}")

    # Return a StreamingResponse with the event_generator
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/", response_model=IssueOut)
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_role(["REPORTER", "MAINTAINER", "ADMIN"])),
):
    """
    Creates a new issue and notifies all subscribed SSE clients.
    """
    with REQUEST_TIME.time():
        file_path = None

        if file and file.filename:
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Get file extension safely
            _, ext = os.path.splitext(file.filename)
            safe_ext = ext if ext else ""

            # Create UUID filename
            uuid_filename = f"{uuid4().hex}{safe_ext}"
            file_path = os.path.join(UPLOAD_DIR, uuid_filename)

            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                logger.error(f"Failed to save file: {e}")
                file_path = None

        issue = Issue(
            title=title,
            description=description,
            severity=Severity.LOW,
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
                "severity": "LOW",
                "file_uploaded": bool(file),
            }
        )
        ISSUES_CREATED.inc()

        # --- SSE: Notify connected clients ---
        for client_queue in connected_clients:
            try:
                # Put the issue data into each client's queue
                await client_queue.put(f"Issue created: {issue.title} (id={issue.id})")
            except Exception as e:
                logger.error(f"Failed to send SSE message to client: {e}")
        # --- End SSE notification ---

        return issue


@router.get("/", response_model=List[IssueOut])
def list_issues(db: Session = Depends(get_db), user=Depends(get_current_user)):
    logger.info(
        {"event": "issue_list_requested", "user_id": user.id, "role": user.role.value}
    )

    query = db.query(Issue).options(joinedload(Issue.reporter))

    if user.role.value == UserRole.REPORTER.value:
        return query.filter(Issue.reporter_id == user.id).all()
    return query.all()


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
async def update_issue(
    issue_id: int,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
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
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # Allow all users to update title/description
    if payload.title is not None:
        issue.title = payload.title
    if payload.description is not None:
        issue.description = payload.description

    # Only MAINTAINER and ADMIN can update status/severity
    if payload.status is not None:
        if user.role not in ("MAINTAINER", "ADMIN"):
            logger.info(
                {
                    "event": "issue_update_forbidden_status",
                    "issue_id": issue_id,
                    "user_id": user.id,
                    "role": user.role,
                }
            )
            # raise HTTPException(
            #     status.HTTP_403_FORBIDDEN,
            #     detail="Insufficient permissions to update status.",
            # )
        issue.status = payload.status

    if payload.severity is not None:
        if user.role not in ("MAINTAINER", "ADMIN"):
            logger.info(
                {
                    "event": "issue_update_forbidden_severity",
                    "issue_id": issue_id,
                    "user_id": user.id,
                    "role": user.role,
                }
            )
            # raise HTTPException(
            #     status.HTTP_403_FORBIDDEN,
            #     detail="Insufficient permissions to update severity.",
            # )
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

    # --- SSE: Notify connected clients ---
    for client_queue in connected_clients:
        try:
            # Put the issue data into each client's queue
            await client_queue.put(f"Issue updated: {issue.title} (id={issue.id})")
        except Exception as e:
            logger.error(f"Failed to send SSE message to client: {e}")
    # --- End SSE notification ---

    return issue


@router.delete("/{issue_id}")
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(["ADMIN"])),
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
        raise HTTPException(status_code=404, detail="Issue not found")

    # Delete attached file if it exists
    if issue.file_path:
        try:
            os.remove(issue.file_path)
            logger.info(
                {
                    "event": "file_deleted",
                    "file_path": issue.file_path,
                    "issue_id": issue_id,
                }
            )
        except FileNotFoundError:
            logger.warning(
                {
                    "event": "file_not_found_on_delete",
                    "file_path": issue.file_path,
                    "issue_id": issue_id,
                }
            )
        except Exception as e:
            logger.error(
                {
                    "event": "file_delete_error",
                    "file_path": issue.file_path,
                    "issue_id": issue_id,
                    "error": str(e),
                }
            )

    db.delete(issue)
    db.commit()

    logger.info({"event": "issue_deleted", "issue_id": issue_id, "user_id": user.id})

    # --- SSE: Notify connected clients ---
    for client_queue in connected_clients:
        try:
            await client_queue.put(f"Issue deleted: {issue.title} (id={issue.id})")
        except Exception as e:
            logger.error(f"Failed to send SSE message to client: {e}")
    # --- End SSE notification ---

    return {"detail": "Deleted"}
