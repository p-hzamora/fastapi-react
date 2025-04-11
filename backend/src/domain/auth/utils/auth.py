from datetime import UTC, datetime, timedelta
from typing import Optional
import uuid
import jwt
from passlib.context import CryptContext

from src.env import BACKEND_SECRET_KEY

# openssl rand -hex 32
SESSION_SECRET = BACKEND_SECRET_KEY
ALGORITHM = "HS256"


##############
# Auth Utils
##############


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: Optional[str] = None):
    return (
        pwd_context.verify(plain_password, hashed_password) if hashed_password else None
    )


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
        payload.update({"exp": expire})

    encoded_jwt = jwt.encode(payload, SESSION_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded = jwt.decode(token, SESSION_SECRET, algorithms=[ALGORITHM])
        return decoded
    except Exception:
        return None


def extract_token_from_auth_header(auth_header: str):
    return auth_header[len("Bearer ") :]


def create_api_key():
    key = str(uuid.uuid4()).replace("-", "")
    return f"sk-{key}"
