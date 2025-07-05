from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.jwt import decode_access_token
from db import get_db
from models.user import User
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter_by(email=payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(required: list[str]):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role.value not in required:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return wrapper


def require_sse_user(token: str, db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_current_user(token, db)
    if not user or user.role.value not in ("MAINTAINER", "ADMIN"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return user
