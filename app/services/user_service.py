from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate
from app.utils.security import hash_password
from app.utils.exceptions import NotFoundException, ConflictException


def get_all_users(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users, total


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotFoundException(f"User with id {user_id} not found")
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)

    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != user.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise ConflictException(f"Email '{update_data['email']}' is already in use")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User:
    user = get_user_by_id(db, user_id)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
