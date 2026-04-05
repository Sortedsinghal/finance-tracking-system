from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.exceptions import (
    ConflictException,
    UnauthorizedException,
    BadRequestException,
)


def register_user(db: Session, data: UserCreate) -> User:
    # Check for duplicate username
    if db.query(User).filter(User.username == data.username).first():
        raise ConflictException(f"Username '{data.username}' is already taken")

    if db.query(User).filter(User.email == data.email).first():
        raise ConflictException(f"Email '{data.email}' is already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> TokenResponse:
    user = db.query(User).filter(User.username == data.username).first()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedException("Invalid username or password")

    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        role=user.role.value,
        username=user.username,
        full_name=user.full_name,
    )
