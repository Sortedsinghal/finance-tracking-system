"""
Tests for authentication endpoints.
"""

import pytest
from tests.conftest import get_auth_header


class TestRegister:
    """POST /api/auth/register"""

    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
            "full_name": "New User",
            "role": "viewer",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@test.com"
        assert data["role"] == "viewer"
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, admin_user):
        response = client.post("/api/auth/register", json={
            "username": "testadmin",
            "email": "different@test.com",
            "password": "password123",
            "full_name": "Duplicate",
        })
        assert response.status_code == 409

    def test_register_duplicate_email(self, client, admin_user):
        response = client.post("/api/auth/register", json={
            "username": "differentuser",
            "email": "admin@test.com",
            "password": "password123",
            "full_name": "Duplicate",
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "username": "baduser",
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Bad User",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/auth/register", json={
            "username": "shortpw",
            "email": "short@test.com",
            "password": "123",
            "full_name": "Short PW",
        })
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={
            "username": "incomplete",
        })
        assert response.status_code == 422


class TestLogin:
    """POST /api/auth/login"""

    def test_login_success(self, client, admin_user):
        response = client.post("/api/auth/login", json={
            "username": "testadmin",
            "password": "admin123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"
        assert data["username"] == "testadmin"

    def test_login_wrong_password(self, client, admin_user):
        response = client.post("/api/auth/login", json={
            "username": "testadmin",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "username": "ghost",
            "password": "password123",
        })
        assert response.status_code == 401


class TestGetMe:
    """GET /api/auth/me"""

    def test_get_me_authenticated(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testadmin"

    def test_get_me_unauthenticated(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalidtoken123",
        })
        assert response.status_code == 401
