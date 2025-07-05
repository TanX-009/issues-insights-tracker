from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models.user import User, UserOut, UserRole
from core.security import hash_password, verify_password
from core.jwt import create_access_token
from core.logging import logger

router = APIRouter()


class AuthRequest(BaseModel):
    email: str
    password: str


# --- New: AuthResponse Model ---
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut  # Include the UserOut model


@router.post("/signup", response_model=AuthResponse)
def signup(auth: AuthRequest, db: Session = Depends(get_db)):
    logger.info({"event": "signup_attempt", "email": auth.email})

    user = db.query(User).filter_by(email=auth.email).first()
    if user:
        logger.warning({"event": "signup_failed_email_exists", "email": auth.email})
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=auth.email,
        password_hash=hash_password(auth.password),
        role=UserRole.REPORTER,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(
        {
            "event": "signup_success",
            "user_id": new_user.id,
            "email": new_user.email,
            "role": new_user.role.value,
        }
    )

    token = create_access_token({"sub": new_user.email, "role": new_user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(new_user),
    }


@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    logger.info({"event": "login_attempt", "email": form_data.username})

    user = db.query(User).filter_by(email=form_data.username).first()
    if not user or not verify_password(form_data.password, str(user.password_hash)):
        logger.warning({"event": "login_failed", "email": form_data.username})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info(
        {
            "event": "login_success",
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
        }
    )

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
    }
