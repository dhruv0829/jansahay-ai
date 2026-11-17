from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.config import settings
from app.models.models import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserOut
from app.services.auth_service import (
    hash_password, verify_password, password_needs_rehash,
    create_access_token, get_current_user, set_session_cookie, clear_session_cookie,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=str(new_user.id))
    set_session_cookie(response, token)
    user_out = UserOut(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_admin=new_user.is_admin,
        has_profile=False
    )
    return Token(access_token=token if settings.APP_ENV != "production" else "", user=user_out)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive."
        )

    if password_needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(credentials.password)
        db.commit()

    token = create_access_token(subject=str(user.id))
    set_session_cookie(response, token)
    has_profile = user.profile is not None
    user_out = UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        has_profile=has_profile
    )
    return Token(access_token=token if settings.APP_ENV != "production" else "", user=user_out)


@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"status": "signed_out"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        has_profile=current_user.profile is not None
    )
