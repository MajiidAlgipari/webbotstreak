from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("", response_model=list[schemas.MessageOut])
def list_messages(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.MessageTemplate).filter(models.MessageTemplate.user_id == user.id).all()


@router.post("", response_model=schemas.MessageOut)
def add_message(payload: schemas.MessageCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = models.MessageTemplate(user_id=user.id, text=payload.text.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.patch("/{message_id}", response_model=schemas.MessageOut)
def update_message(message_id: int, payload: schemas.MessageUpdate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.query(models.MessageTemplate).filter(models.MessageTemplate.id == message_id, models.MessageTemplate.user_id == user.id).first()
    if not msg:
        raise HTTPException(404, "Pesan tidak ditemukan")
    if payload.text is not None:
        msg.text = payload.text.strip()
    if payload.is_active is not None:
        msg.is_active = payload.is_active
    db.commit()
    db.refresh(msg)
    return msg


@router.delete("/{message_id}")
def delete_message(message_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.query(models.MessageTemplate).filter(models.MessageTemplate.id == message_id, models.MessageTemplate.user_id == user.id).first()
    if not msg:
        raise HTTPException(404, "Pesan tidak ditemukan")
    db.delete(msg)
    db.commit()
    return {"ok": True}
