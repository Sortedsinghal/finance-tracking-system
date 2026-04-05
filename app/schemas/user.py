"""
Pydantic schemas for user-related requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from app.models.user import UserRole


# ── Auth / Login ─────────────────────────────────────────
class LoginRequest(BaseModel):
    """Credentials submitted for login."""
    username: str = Field(..., min_length=3, max_length=50, examples=["admin"])
    password: str = Field(..., min_length=6, examples=["admin123"])


class TokenResponse(BaseModel):
    """JWT token returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: str


# ── User CRUD ────────────────────────────────────────────
class UserCreate(BaseModel):
    """Payload for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, examples=["johndoe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["securepass123"])
    full_name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    role: UserRole = Field(default=UserRole.VIEWER, examples=["viewer"])


class UserUpdate(BaseModel):
    """Payload for updating a user (all fields optional)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User data returned to the client (excludes password)."""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated user list."""
    users: list[UserResponse]
    total: int
