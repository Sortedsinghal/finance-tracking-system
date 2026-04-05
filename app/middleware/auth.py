"""
Authentication middleware — JWT verification and role-based access dependencies.
"""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole, ROLE_HIERARCHY
from app.utils.security import decode_access_token
from app.utils.exceptions import UnauthorizedException, ForbiddenException

# ── Bearer token extractor ───────────────────────────────
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extract and validate the JWT from the
    Authorization header, then return the corresponding User object.
    """
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    username: str | None = payload.get("sub")
    if username is None:
        raise UnauthorizedException("Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")

    return user


# ── Role-based dependency factories ─────────────────────
def require_role(minimum_role: UserRole):
    """
    Returns a FastAPI dependency that enforces a minimum role level.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role(minimum_role):
            raise ForbiddenException(
                f"This action requires at least '{minimum_role.value}' role. "
                f"Your role is '{current_user.role.value}'."
            )
        return current_user

    return role_checker


# Convenience dependencies
require_viewer = require_role(UserRole.VIEWER)
require_analyst = require_role(UserRole.ANALYST)
require_admin = require_role(UserRole.ADMIN)
