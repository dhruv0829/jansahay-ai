import hmac
import hashlib
import json
import base64
import secrets
import time
from typing import Optional
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User
from app.config import settings

security = HTTPBearer(auto_error=False)

PASSWORD_HASH_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Create a PBKDF2-SHA256 password hash with a unique random salt."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PASSWORD_HASH_ITERATIONS
    )
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split("$")
        if len(parts) == 4 and parts[0] == "pbkdf2_sha256":
            iterations = int(parts[1])
            salt = bytes.fromhex(parts[2])
            expected_hex = parts[3]
        elif len(parts) == 3 and parts[0].startswith("pbkdf2:sha256:"):
            # Accept the legacy application hashes so existing accounts can
            # log in once and be upgraded to an individually salted hash.
            iterations = int(parts[0].rsplit(":", 1)[1])
            salt = parts[1].encode("utf-8")
            expected_hex = parts[2]
        else:
            return False
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            iterations
        )
        return hmac.compare_digest(key.hex(), expected_hex)
    except Exception:
        return False


def password_needs_rehash(hashed_password: str) -> bool:
    return not hashed_password.startswith(f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}$")

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))

def create_access_token(subject: str, expires_delta_minutes: Optional[int] = None) -> str:
    if expires_delta_minutes is None:
        expires_delta_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    exp = int(time.time()) + (expires_delta_minutes * 60)
    
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": str(subject), "exp": exp, "iat": int(time.time())}
    
    h_b64 = _b64_encode(json.dumps(header).encode('utf-8'))
    p_b64 = _b64_encode(json.dumps(payload).encode('utf-8'))
    
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        f"{h_b64}.{p_b64}".encode('utf-8'),
        hashlib.sha256
    ).digest()
    s_b64 = _b64_encode(signature)
    
    return f"{h_b64}.{p_b64}.{s_b64}"


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="jansahay_session",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key="jansahay_session",
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/",
    )

def decode_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        h_b64, p_b64, s_b64 = parts
        header = json.loads(_b64_decode(h_b64).decode('utf-8'))
        if header.get("alg") != settings.ALGORITHM or header.get("typ") != "JWT":
            return None
        
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f"{h_b64}.{p_b64}".encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(_b64_encode(expected_sig), s_b64):
            return None
            
        payload = json.loads(_b64_decode(p_b64).decode('utf-8'))
        if not isinstance(payload.get("exp"), (int, float)) or payload["exp"] <= time.time():
            return None
        if not isinstance(payload.get("sub"), str) or not payload["sub"].isdigit():
            return None
        return payload
    except Exception:
        return None

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(default=None, alias="jansahay_session"),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials if credentials and credentials.credentials else access_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        
    return user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(default=None, alias="jansahay_session"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = credentials.credentials if credentials and credentials.credentials else access_token
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    try:
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            return user if user and user.is_active else None
    except Exception:
        return None
    return None

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return current_user
