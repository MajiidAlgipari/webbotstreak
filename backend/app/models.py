import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    friends = relationship("Friend", back_populates="owner", cascade="all, delete-orphan")
    templates = relationship("MessageTemplate", back_populates="owner", cascade="all, delete-orphan")
    logs = relationship("StreakLog", back_populates="owner", cascade="all, delete-orphan")
    session = relationship("TikTokSession", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class TikTokSession(Base):
    """Menyimpan storage_state (auth.json) milik tiap user, terenkripsi di kolom `data`."""
    __tablename__ = "tiktok_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    encrypted_data = Column(Text, nullable=False)  # auth.json terenkripsi
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_valid = Column(Boolean, default=True)  # false kalau login expired

    owner = relationship("User", back_populates="session")


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    display_name = Column(String(255), nullable=False)  # nama persis di TikTok
    is_selected = Column(Boolean, default=True)  # ikut dikirimi streak atau tidak
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="friends")


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="templates")


class StreakStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class StreakLog(Base):
    __tablename__ = "streak_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_name = Column(String(255), nullable=False)
    message_sent = Column(String(255), nullable=True)
    status = Column(Enum(StreakStatus), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="logs")
