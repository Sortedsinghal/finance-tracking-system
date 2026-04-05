"""
Tests for user management endpoints (admin only).
"""

import pytest
from tests.conftest import get_auth_header


class TestListUsers:
    """GET /api/users"""

    def test_list_as_admin(self, client, admin_user, viewer_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        usernames = [u["username"] for u in data["users"]]
        assert "testadmin" in usernames

    def test_list_as_viewer_forbidden(self, client, viewer_user):
        headers = get_auth_header(client, "testviewer", "viewer123")
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403

    def test_list_as_analyst_forbidden(self, client, analyst_user):
        headers = get_auth_header(client, "testanalyst", "analyst123")
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 403


class TestGetUser:
    """GET /api/users/{id}"""

    def test_get_user_by_id(self, client, admin_user, viewer_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.get(f"/api/users/{viewer_user.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testviewer"

    def test_get_nonexistent_user(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.get("/api/users/9999", headers=headers)
        assert response.status_code == 404


class TestUpdateUser:
    """PUT /api/users/{id}"""

    def test_update_role(self, client, admin_user, viewer_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.put(f"/api/users/{viewer_user.id}", json={
            "role": "analyst",
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == "analyst"

    def test_update_email(self, client, admin_user, viewer_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.put(f"/api/users/{viewer_user.id}", json={
            "email": "updated@test.com",
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "updated@test.com"


class TestDeactivateUser:
    """DELETE /api/users/{id}"""

    def test_deactivate_user(self, client, admin_user, viewer_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.delete(f"/api/users/{viewer_user.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_deactivate_nonexistent(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.delete("/api/users/9999", headers=headers)
        assert response.status_code == 404
