"""
Tests for transaction CRUD, filtering, and role restrictions.
"""

import pytest
from tests.conftest import get_auth_header


SAMPLE_TRANSACTION = {
    "amount": 1500.00,
    "type": "income",
    "category": "Salary",
    "date": "2024-09-15",
    "description": "Monthly salary",
}


class TestCreateTransaction:
    """POST /api/transactions"""

    def test_create_as_admin(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 1500.00
        assert data["type"] == "income"
        assert data["category"] == "Salary"

    def test_create_as_viewer_forbidden(self, client, viewer_user):
        headers = get_auth_header(client, "testviewer", "viewer123")
        response = client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        assert response.status_code == 403

    def test_create_as_analyst_forbidden(self, client, analyst_user):
        headers = get_auth_header(client, "testanalyst", "analyst123")
        response = client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        assert response.status_code == 403

    def test_create_invalid_amount(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        bad_data = {**SAMPLE_TRANSACTION, "amount": -100}
        response = client.post("/api/transactions", json=bad_data, headers=headers)
        assert response.status_code == 422

    def test_create_missing_fields(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.post("/api/transactions", json={"amount": 100}, headers=headers)
        assert response.status_code == 422

    def test_create_unauthenticated(self, client):
        response = client.post("/api/transactions", json=SAMPLE_TRANSACTION)
        assert response.status_code == 401


class TestListTransactions:
    """GET /api/transactions"""

    def test_list_empty(self, client, viewer_user):
        headers = get_auth_header(client, "testviewer", "viewer123")
        response = client.get("/api/transactions", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_list_with_data(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        # Create a transaction
        client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        # List
        response = client.get("/api/transactions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["transactions"]) == 1

    def test_filter_by_type(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        client.post("/api/transactions", json={**SAMPLE_TRANSACTION, "type": "expense", "category": "Rent"}, headers=headers)

        response = client.get("/api/transactions?type=income", headers=headers)
        assert response.json()["total"] == 1

        response = client.get("/api/transactions?type=expense", headers=headers)
        assert response.json()["total"] == 1

    def test_pagination(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        for i in range(5):
            client.post("/api/transactions", json={
                **SAMPLE_TRANSACTION,
                "amount": 100 + i,
                "date": f"2024-09-{10 + i:02d}",
            }, headers=headers)

        response = client.get("/api/transactions?page=1&page_size=2", headers=headers)
        data = response.json()
        assert data["total"] == 5
        assert len(data["transactions"]) == 2
        assert data["total_pages"] == 3


class TestUpdateTransaction:
    """PUT /api/transactions/{id}"""

    def test_update_success(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        create_res = client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        txn_id = create_res.json()["id"]

        response = client.put(f"/api/transactions/{txn_id}", json={
            "amount": 2000.00,
            "description": "Updated salary",
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["amount"] == 2000.00
        assert response.json()["description"] == "Updated salary"

    def test_update_nonexistent(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.put("/api/transactions/9999", json={"amount": 100}, headers=headers)
        assert response.status_code == 404


class TestDeleteTransaction:
    """DELETE /api/transactions/{id}"""

    def test_delete_success(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        create_res = client.post("/api/transactions", json=SAMPLE_TRANSACTION, headers=headers)
        txn_id = create_res.json()["id"]

        response = client.delete(f"/api/transactions/{txn_id}", headers=headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/transactions/{txn_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_nonexistent(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        response = client.delete("/api/transactions/9999", headers=headers)
        assert response.status_code == 404
