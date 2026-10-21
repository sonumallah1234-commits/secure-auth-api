from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.core.rate_limit import login_rate_limit
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserRegister, UserResponse
from app.services.auth import (
    authenticate_user,
    build_access_token,
    build_reset_token,
    create_user,
    reset_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        user = create_user(db, payload, role="USER")
    except ValueError as exc:
        field = str(exc)
        if field == "username":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists") from exc
        if field == "email":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists") from exc
        raise

    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), _rate_limit: None = Depends(login_rate_limit)):
    user = authenticate_user(db, payload)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=build_access_token(user))


@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), _rate_limit: None = Depends(login_rate_limit)):
    user = authenticate_user(
        db,
        LoginRequest(
            username_or_email=form_data.username,
            password=form_data.password,
        ),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=build_access_token(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return ForgotPasswordResponse(detail="If the email exists, a reset token was generated")

    reset_token = build_reset_token(user)
    return ForgotPasswordResponse(
        detail="Reset token generated",
        reset_token=reset_token,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_user_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        reset_password(db, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from exc
    except HTTPException:
        raise

    return MessageResponse(detail="Password updated successfully")


@router.post("/logout", response_model=MessageResponse)
def logout():
    return MessageResponse(detail="Token should be discarded by the client")