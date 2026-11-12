from sqlalchemy.orm import Session

from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.core.security import hash_password, verify_password
from backend.core.exceptions import ValidationError, NotFoundError
from datetime import datetime, timedelta, timezone

from backend.core.security import generate_reset_token, hash_password
from backend.core.config import settings


def register_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValidationError("An account with this email already exists")

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValidationError("Incorrect email or password")
    return user


RESET_TOKEN_EXPIRE_MINUTES = 30


def request_password_reset(db: Session, email: str) -> str | None:
    """
    Generates and stores a reset token for the given email.
    Returns the token ONLY if the user exists (used for dev-mode response).
    Always behaves the same from the outside regardless of whether the email
    exists, to avoid leaking which emails are registered.
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None  # caller returns a generic message either way

    token = generate_reset_token()
    user.reset_token = token
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    db.commit()

    return token


def reset_password(db: Session, reset_token: str, new_password: str) -> None:
    user = db.query(User).filter(User.reset_token == reset_token).first()

    if user is None:
        raise ValidationError("Invalid or expired reset token")

    expires_at = user.reset_token_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise ValidationError("Invalid or expired reset token")

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()