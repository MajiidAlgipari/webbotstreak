from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.patch("/users/{user_id}/toggle-active")
def toggle_active(user_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(404, "User tidak ditemukan")
    if target.id == admin.id:
        raise HTTPException(400, "Tidak bisa menonaktifkan akun sendiri")
    target.is_active = not target.is_active
    db.commit()
    return {"ok": True, "is_active": target.is_active}


@router.get("/logs", response_model=list[schemas.StreakLogOut])
def all_logs(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.StreakLog).order_by(models.StreakLog.created_at.desc()).limit(300).all()
