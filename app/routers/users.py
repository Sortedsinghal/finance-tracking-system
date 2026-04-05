from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user,
    deactivate_user,
)

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users, total = get_all_users(db, skip=skip, limit=limit)
    return UserListResponse(users=users, total=total)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a single user",
)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return update_user(db, user_id, data)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Deactivate a user",
)
def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return deactivate_user(db, user_id)
