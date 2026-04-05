"""
Pydantic schemas for analytics / summary responses.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class FinancialSummary(BaseModel):
    """High-level financial overview."""
    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int
    income_count: int
    expense_count: int


class CategoryBreakdownItem(BaseModel):
    """Single category in the breakdown."""
    category: str
    total: float
    count: int
    percentage: float


class CategoryBreakdown(BaseModel):
    """Income and expense breakdown by category."""
    income_categories: list[CategoryBreakdownItem]
    expense_categories: list[CategoryBreakdownItem]


class MonthlyTrendItem(BaseModel):
    """Financial totals for a single month."""
    month: str  # "YYYY-MM"
    income: float
    expenses: float
    net: float


class MonthlyTrend(BaseModel):
    """Monthly financial trends over time."""
    trends: list[MonthlyTrendItem]


class RecentActivityItem(BaseModel):
    """Single item in recent activity feed."""
    id: int
    amount: float
    type: str
    category: str
    date: date
    description: Optional[str]


class RecentActivity(BaseModel):
    """Most recent transactions."""
    transactions: list[RecentActivityItem]


class DashboardData(BaseModel):
    """Combined dashboard payload — everything the frontend needs."""
    summary: FinancialSummary
    category_breakdown: CategoryBreakdown
    monthly_trends: MonthlyTrend
    recent_activity: RecentActivity
