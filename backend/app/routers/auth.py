from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user, COOKIE_NAME

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_MAX_AGE = 60 * 60 * 8  # 8 jam


@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == payload.username).first()
    if existing:
        raise HTTPException(400, "Username sudah dipakai")

    # User pertama yang daftar otomatis jadi admin
    is_first_user = db.query(models.User).count() == 0
    user = models.User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=models.UserRole.admin if is_first_user else models.UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.UserOut)
def login(payload: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Username atau password salah")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Akun dinonaktifkan, hubungi admin")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=True,       # set True saat production (HTTPS). Set False kalau tes di http://localhost
        max_age=COOKIE_MAX_AGE,
    )
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
