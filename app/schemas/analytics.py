from datetime import date
from typing import Optional

from pydantic import BaseModel


class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int
    income_count: int
    expense_count: int


class CategoryBreakdownItem(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class CategoryBreakdown(BaseModel):
    income_categories: list[CategoryBreakdownItem]
    expense_categories: list[CategoryBreakdownItem]


class MonthlyTrendItem(BaseModel):
    month: str  # "YYYY-MM"
    income: float
    expenses: float
    net: float


class MonthlyTrend(BaseModel):
    trends: list[MonthlyTrendItem]


class RecentActivityItem(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    description: Optional[str]


class RecentActivity(BaseModel):
    transactions: list[RecentActivityItem]


class DashboardData(BaseModel):
    summary: FinancialSummary
    category_breakdown: CategoryBreakdown
    monthly_trends: MonthlyTrend
    recent_activity: RecentActivity
