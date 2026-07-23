from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/api/friends", tags=["friends"])


@router.get("", response_model=list[schemas.FriendOut])
def list_friends(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Friend).filter(models.Friend.user_id == user.id).all()


@router.post("", response_model=schemas.FriendOut)
def add_friend(payload: schemas.FriendCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend = models.Friend(user_id=user.id, display_name=payload.display_name.strip())
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend


@router.patch("/{friend_id}", response_model=schemas.FriendOut)
def update_friend(friend_id: int, payload: schemas.FriendUpdate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id, models.Friend.user_id == user.id).first()
    if not friend:
        raise HTTPException(404, "Teman tidak ditemukan")
    if payload.is_selected is not None:
        friend.is_selected = payload.is_selected
    if payload.display_name is not None:
        friend.display_name = payload.display_name.strip()
    db.commit()
    db.refresh(friend)
    return friend


@router.delete("/{friend_id}")
def delete_friend(friend_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id, models.Friend.user_id == user.id).first()
    if not friend:
        raise HTTPException(404, "Teman tidak ditemukan")
    db.delete(friend)
    db.commit()
    return {"ok": True}
