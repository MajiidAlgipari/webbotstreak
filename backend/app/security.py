import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from jose import jwt, JWTError
from passlib.context import CryptContext

# ==== KONFIGURASI (ganti lewat environment variable saat deploy!) ====
JWT_SECRET = os.getenv("JWT_SECRET", "ganti-ini-dengan-random-string-panjang")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Kunci enkripsi untuk auth.json TikTok tiap user (Fernet butuh base64 32 byte)
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    # Hanya untuk dev lokal. WAJIB set FERNET_KEY sendiri saat production
    # (generate sekali dengan: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    FERNET_KEY = Fernet.generate_key().decode()

fernet = Fernet(FERNET_KEY.encode())
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_minutes: int = JWT_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


def encrypt_text(plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str) -> str:
    return fernet.decrypt(encrypted_text.encode()).decode()
