from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class FriendCreate(BaseModel):
    display_name: str


class FriendUpdate(BaseModel):
    is_selected: Optional[bool] = None
    display_name: Optional[str] = None


class FriendOut(BaseModel):
    id: int
    display_name: str
    is_selected: bool

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    text: str


class MessageUpdate(BaseModel):
    text: Optional[str] = None
    is_active: Optional[bool] = None


class MessageOut(BaseModel):
    id: int
    text: str
    is_active: bool

    class Config:
        from_attributes = True


class StreakLogOut(BaseModel):
    id: int
    friend_name: str
    message_sent: Optional[str]
    status: str
    detail: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StreakStatusOut(BaseModel):
    is_lit: bool          # api nyala hari ini atau tidak
    last_run_at: Optional[datetime]
    total_friends: int
    sent_today: int
    failed_today: int


class TikTokSessionIn(BaseModel):
    auth_json: str  # isi file auth.json (hasil export cookies/storage_state), sebagai string JSON
