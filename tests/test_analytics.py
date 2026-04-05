"""
Tests for analytics endpoints.
"""

import pytest
from tests.conftest import get_auth_header


def seed_transactions(client, headers):
    """Helper: seed a set of transactions for analytics tests."""
    records = [
        {"amount": 5000, "type": "income", "category": "Salary", "date": "2024-09-01", "description": "Sept salary"},
        {"amount": 1200, "type": "income", "category": "Freelance", "date": "2024-09-15", "description": "Web project"},
        {"amount": 1500, "type": "expense", "category": "Rent", "date": "2024-09-01", "description": "Monthly rent"},
        {"amount": 300, "type": "expense", "category": "Groceries", "date": "2024-09-10", "description": "Grocery shopping"},
        {"amount": 100, "type": "expense", "category": "Utilities", "date": "2024-09-15", "description": "Electric bill"},
        {"amount": 5000, "type": "income", "category": "Salary", "date": "2024-10-01", "description": "Oct salary"},
        {"amount": 1500, "type": "expense", "category": "Rent", "date": "2024-10-01", "description": "Monthly rent"},
    ]
    for r in records:
        client.post("/api/transactions", json=r, headers=headers)


class TestFinancialSummary:
    """GET /api/analytics/summary"""

    def test_summary_with_data(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        seed_transactions(client, headers)

        response = client.get("/api/analytics/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == 11200.0
        assert data["total_expenses"] == 3400.0
        assert data["balance"] == 7800.0
        assert data["transaction_count"] == 7
        assert data["income_count"] == 3
        assert data["expense_count"] == 4

    def test_summary_empty(self, client, viewer_user):
        headers = get_auth_header(client, "testviewer", "viewer123")
        response = client.get("/api/analytics/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == 0
        assert data["balance"] == 0

    def test_summary_unauthenticated(self, client):
        response = client.get("/api/analytics/summary")
        assert response.status_code == 401


class TestCategoryBreakdown:
    """GET /api/analytics/categories"""

    def test_categories_as_analyst(self, client, admin_user, analyst_user):
        admin_headers = get_auth_header(client, "testadmin", "admin123")
        seed_transactions(client, admin_headers)

        analyst_headers = get_auth_header(client, "testanalyst", "analyst123")
        response = client.get("/api/analytics/categories", headers=analyst_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["income_categories"]) > 0
        assert len(data["expense_categories"]) > 0
        # Check percentages sum to ~100
        income_pct = sum(c["percentage"] for c in data["income_categories"])
        assert 99 <= income_pct <= 101

    def test_categories_as_viewer_forbidden(self, client, viewer_user):
        headers = get_auth_header(client, "testviewer", "viewer123")
        response = client.get("/api/analytics/categories", headers=headers)
        assert response.status_code == 403


class TestMonthlyTrends:
    """GET /api/analytics/monthly"""

    def test_monthly_trends(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        seed_transactions(client, headers)

        response = client.get("/api/analytics/monthly", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["trends"]) == 2  # September and October
        sept = data["trends"][0]
        assert sept["month"] == "2024-09"
        assert sept["income"] == 6200.0
        assert sept["expenses"] == 1900.0


class TestDashboard:
    """GET /api/analytics/dashboard"""

    def test_dashboard_combined(self, client, admin_user):
        headers = get_auth_header(client, "testadmin", "admin123")
        seed_transactions(client, headers)

        response = client.get("/api/analytics/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "category_breakdown" in data
        assert "monthly_trends" in data
        assert "recent_activity" in data
