from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from db import get_db
from models.user import User, UserOut, UserRole
from core.security import hash_password
from dependencies import require_role
from core.logging import logger

router = APIRouter()


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UpdateUserRequest(BaseModel):
    password: Optional[str] = None
    role: Optional[UserRole] = None


@router.post("/", response_model=UserOut)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role(["ADMIN"])),
):
    logger.info(
        {"event": "create_user_attempt", "admin_id": user.id, "email": payload.email}
    )

    existing = db.query(User).filter_by(email=payload.email).first()
    if existing:
        logger.warning({"event": "create_user_conflict", "email": payload.email})
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info({"event": "create_user_success", "user_id": new_user.id})
    return UserOut.model_validate(new_user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role(["ADMIN"])),
):
    target_user = db.query(User).get(user_id)
    if not target_user:
        logger.warning({"event": "update_user_not_found", "user_id": user_id})
        raise HTTPException(status_code=404, detail="User not found")

    if payload.password:
        target_user.password_hash = hash_password(payload.password)
    if payload.role:
        target_user.role = payload.role

    db.commit()
    db.refresh(target_user)

    logger.info({"event": "update_user_success", "user_id": user_id})
    return UserOut.model_validate(target_user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role(["ADMIN"])),
):
    target_user = db.query(User).get(user_id)
    if not target_user:
        logger.warning({"event": "delete_user_not_found", "user_id": user_id})
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(target_user)
    db.commit()

    logger.info({"event": "delete_user_success", "user_id": user_id})
    return {"detail": f"User {user_id} deleted successfully"}


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    user=Depends(require_role(["ADMIN"])),
):
    logger.info({"event": "list_users_requested", "admin_id": user.id})
    return db.query(User).all()
