from datetime import UTC, datetime, timedelta
from typing import Annotated, Optional
import uuid
import jwt
from fastapi import Request, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from src.constants import ERROR_MESSAGES

from src.domain.user.models import Users, UserModel
from src.env import BACKEND_SECRET_KEY

# openssl rand -hex 32
SESSION_SECRET = BACKEND_SECRET_KEY
ALGORITHM = "HS256"


##############
# Auth Utils
##############


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_security = HTTPBearer(auto_error=False)


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


def get_current_user(
    request: Request,
    background_tasks:BackgroundTasks,
    auth_token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> UserModel:
    token = None
    if auth_token is not None:
        token = auth_token.credentials

    if token is None and "token" in request.cookies:
        token = request.cookies["token"]

    if token is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    # auth by api key
    if token.startswith("sk-"):
        if not request.state.enable_api_key:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.API_KEY_NOT_ALLOWED
            )

        return get_current_user_by_api_key(token)
    
    # auth by jwt token
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if data is not None and "id" in data:
        user = Users.get_user_by_id(data["id"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.INVALID_TOKEN,
            )
        else:
            # Refresh the user's last active timestamp asynchronously
            # to prevent blocking the request
            if background_tasks:
                background_tasks.add_task(Users.update_user_last_active_by_id, user.id)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )


def get_current_user_by_api_key(api_key: str):
    user = Users.get_user_by_api_key(api_key)

    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.INVALID_TOKEN
        )
    Users.update_user_last_active_by_id(user.id)

    return user


def get_verified_user(user: Annotated[UserModel, Depends(get_current_user)]):
    if user.role not in {"users", "admin"}:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )
    return user


def get_admin_user(user: Annotated[UserModel, Depends(get_current_user)]) -> UserModel:
    if user.role != "admin":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )
    return user
