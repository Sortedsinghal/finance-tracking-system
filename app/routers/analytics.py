from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_viewer, require_analyst
from app.models.user import User
from app.schemas.analytics import (
    FinancialSummary,
    CategoryBreakdown,
    MonthlyTrend,
    RecentActivity,
    DashboardData,
)
from app.services.analytics_service import (
    get_financial_summary,
    get_category_breakdown,
    get_monthly_trends,
    get_recent_activity,
    get_dashboard_data,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    response_model=FinancialSummary,
    summary="Financial summary",
    description="Get total income, expenses, and balance. Requires viewer role or above.",
)
def summary(
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    return get_financial_summary(db, date_from, date_to)


@router.get(
    "/categories",
    response_model=CategoryBreakdown,
    summary="Category breakdown",
    description="Income and expense totals broken down by category. Requires analyst role or above.",
)
def categories(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
):
    return get_category_breakdown(db, date_from, date_to)


@router.get(
    "/monthly",
    response_model=MonthlyTrend,
    summary="Monthly trends",
    description="Income, expenses, and net totals by month. Requires analyst role or above.",
)
def monthly(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
):
    return get_monthly_trends(db, date_from, date_to)


@router.get(
    "/recent",
    response_model=RecentActivity,
    summary="Recent activity",
    description="Get the most recent transactions. Requires viewer role or above.",
)
def recent(
    limit: int = Query(10, ge=1, le=50, description="Number of transactions"),
    current_user: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    return get_recent_activity(db, limit)


@router.get(
    "/dashboard",
    response_model=DashboardData,
    summary="Dashboard data",
    description="Combined payload with summary, categories, trends, and recent activity.",
)
def dashboard(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    return get_dashboard_data(db, date_from, date_to)
