from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from .database import get_db
from .security import decode_access_token
from . import models

COOKIE_NAME = "botstreak_session"


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Belum login")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesi tidak valid, silakan login ulang")

    user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Akun tidak ditemukan / dinonaktifkan")

    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != models.UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Khusus admin")
    return user
