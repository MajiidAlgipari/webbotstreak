from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db, SessionLocal
from ..deps import get_current_user
from ..security import encrypt_text, decrypt_text
from ..worker.tiktok_bot import run_streak_job

router = APIRouter(prefix="/api/streak", tags=["streak"])


@router.post("/connect")
def connect_session(payload: schemas.TikTokSessionIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Simpan isi auth.json (storage_state) milik user, terenkripsi."""
    try:
        import json
        json.loads(payload.auth_json)  # validasi bentuknya JSON valid
    except Exception:
        raise HTTPException(400, "auth_json bukan JSON yang valid")

    existing = db.query(models.TikTokSession).filter(models.TikTokSession.user_id == user.id).first()
    encrypted = encrypt_text(payload.auth_json)
    if existing:
        existing.encrypted_data = encrypted
        existing.is_valid = True
    else:
        existing = models.TikTokSession(user_id=user.id, encrypted_data=encrypted, is_valid=True)
        db.add(existing)
    db.commit()
    return {"ok": True}


@router.get("/status", response_model=schemas.StreakStatusOut)
def get_status(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_friends = db.query(models.Friend).filter(
        models.Friend.user_id == user.id, models.Friend.is_selected == True  # noqa: E712
    ).count()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logs_today = db.query(models.StreakLog).filter(
        models.StreakLog.user_id == user.id, models.StreakLog.created_at >= today_start
    ).all()

    sent_today = sum(1 for l in logs_today if l.status == models.StreakStatus.success)
    failed_today = sum(1 for l in logs_today if l.status == models.StreakStatus.failed)

    last_log = db.query(models.StreakLog).filter(models.StreakLog.user_id == user.id).order_by(
        models.StreakLog.created_at.desc()
    ).first()

    # "Api nyala" = minimal 1 pengiriman sukses hari ini ke tiap teman yang aktif
    is_lit = total_friends > 0 and sent_today >= total_friends

    return schemas.StreakStatusOut(
        is_lit=is_lit,
        last_run_at=last_log.created_at if last_log else None,
        total_friends=total_friends,
        sent_today=sent_today,
        failed_today=failed_today,
    )


@router.get("/logs", response_model=list[schemas.StreakLogOut])
def get_logs(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.StreakLog).filter(models.StreakLog.user_id == user.id).order_by(
        models.StreakLog.created_at.desc()
    ).limit(100).all()


def _execute_job(user_id: int):
    """Dipanggil di background thread: jalankan playwright job & tulis hasil ke DB."""
    db = SessionLocal()
    try:
        session_row = db.query(models.TikTokSession).filter(models.TikTokSession.user_id == user_id).first()
        if not session_row or not session_row.is_valid:
            return

        friends = db.query(models.Friend).filter(
            models.Friend.user_id == user_id, models.Friend.is_selected == True  # noqa: E712
        ).all()
        templates = db.query(models.MessageTemplate).filter(
            models.MessageTemplate.user_id == user_id, models.MessageTemplate.is_active == True  # noqa: E712
        ).all()

        friend_names = [f.display_name for f in friends]
        messages = [t.text for t in templates]

        auth_json = decrypt_text(session_row.encrypted_data)
        result = run_streak_job(auth_json, friend_names, messages)

        if result["session_invalid"]:
            session_row.is_valid = False
            db.commit()
            return

        for r in result["results"]:
            status_enum = {
                "success": models.StreakStatus.success,
                "failed": models.StreakStatus.failed,
                "skipped": models.StreakStatus.skipped,
            }[r["status"]]
            db.add(models.StreakLog(
                user_id=user_id,
                friend_name=r["friend"],
                message_sent=r["message"],
                status=status_enum,
                detail=r["detail"],
            ))
        db.commit()
    finally:
        db.close()


@router.post("/trigger")
def trigger_send(background_tasks: BackgroundTasks, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_row = db.query(models.TikTokSession).filter(models.TikTokSession.user_id == user.id).first()
    if not session_row:
        raise HTTPException(400, "Belum menghubungkan sesi TikTok (auth.json)")
    if not session_row.is_valid:
        raise HTTPException(400, "Sesi TikTok expired, silakan hubungkan ulang")

    background_tasks.add_task(_execute_job, user.id)
    return {"ok": True, "message": "Pengiriman streak dimulai di latar belakang"}
