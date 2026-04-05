from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account. The default role is 'viewer'.",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT token",
    description="Authenticate with username and password to receive a JWT access token.",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return authenticate_user(db, data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
