"""
Test fixtures — shared setup for all test modules.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.utils.security import hash_password

# ── In-memory test database ─────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test_finance.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Raw database session for direct DB operations in tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user and return it."""
    user = User(
        username="testadmin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def analyst_user(db_session):
    """Create an analyst user and return it."""
    user = User(
        username="testanalyst",
        email="analyst@test.com",
        hashed_password=hash_password("analyst123"),
        full_name="Test Analyst",
        role=UserRole.ANALYST,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def viewer_user(db_session):
    """Create a viewer user and return it."""
    user = User(
        username="testviewer",
        email="viewer@test.com",
        hashed_password=hash_password("viewer123"),
        full_name="Test Viewer",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_header(client, username: str, password: str) -> dict:
    """Helper: login and return the Authorization header."""
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
