from backend.api.dependencies import get_current_user
from backend.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.services import auth_service
from backend.core.security import create_access_token
from backend.schemas.user import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest
from backend.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, user_data)
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user



@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token = auth_service.request_password_reset(db, data.email)

    response = ForgotPasswordResponse(
        message="If an account with that email exists, a reset link has been generated."
    )

    # DEVELOPMENT ONLY: since we don't have email sending set up yet, we
    # return the token directly so you can test the flow. In a real
    # production system, this token would be emailed to the user instead,
    # and NEVER returned in the API response.
    if settings.ENVIRONMENT == "development" and token:
        response.reset_token = token

    return response


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.reset_password(db, data.reset_token, data.new_password)
    return {"message": "Password has been reset successfully."}