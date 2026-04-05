"""
Analytics service — financial summaries, category breakdowns, and trends.
"""

from collections import defaultdict
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, case

from app.models.transaction import Transaction, TransactionType
from app.schemas.analytics import (
    FinancialSummary,
    CategoryBreakdown,
    CategoryBreakdownItem,
    MonthlyTrend,
    MonthlyTrendItem,
    RecentActivity,
    RecentActivityItem,
    DashboardData,
)


def _date_filters(date_from: Optional[date] = None, date_to: Optional[date] = None):
    """Build optional date range filter conditions."""
    conditions = []
    if date_from:
        conditions.append(Transaction.date >= date_from)
    if date_to:
        conditions.append(Transaction.date <= date_to)
    return conditions


def get_financial_summary(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> FinancialSummary:
    """
    Calculate high-level financial totals.

    Returns total income, total expenses, current balance, and counts.
    """
    conditions = _date_filters(date_from, date_to)

    query = db.query(
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)),
            0,
        ).label("total_income"),
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)),
            0,
        ).label("total_expenses"),
        func.count(Transaction.id).label("transaction_count"),
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.INCOME, 1), else_=0)),
            0,
        ).label("income_count"),
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.EXPENSE, 1), else_=0)),
            0,
        ).label("expense_count"),
    )

    if conditions:
        query = query.filter(and_(*conditions))

    row = query.one()

    total_income = round(float(row.total_income), 2)
    total_expenses = round(float(row.total_expenses), 2)

    return FinancialSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        balance=round(total_income - total_expenses, 2),
        transaction_count=row.transaction_count,
        income_count=row.income_count,
        expense_count=row.expense_count,
    )


def get_category_breakdown(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> CategoryBreakdown:
    """
    Break down income and expenses by category.

    Each item includes the category name, total amount, count,
    and percentage share within its transaction type.
    """
    conditions = _date_filters(date_from, date_to)

    query = db.query(
        Transaction.type,
        Transaction.category,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    ).group_by(Transaction.type, Transaction.category)

    if conditions:
        query = query.filter(and_(*conditions))

    rows = query.all()

    # Separate income and expense, compute percentages
    income_items: list[CategoryBreakdownItem] = []
    expense_items: list[CategoryBreakdownItem] = []

    income_total = sum(r.total for r in rows if r.type == TransactionType.INCOME)
    expense_total = sum(r.total for r in rows if r.type == TransactionType.EXPENSE)

    for row in rows:
        total = round(float(row.total), 2)
        type_total = income_total if row.type == TransactionType.INCOME else expense_total
        percentage = round((total / type_total * 100) if type_total > 0 else 0, 1)

        item = CategoryBreakdownItem(
            category=row.category,
            total=total,
            count=row.count,
            percentage=percentage,
        )

        if row.type == TransactionType.INCOME:
            income_items.append(item)
        else:
            expense_items.append(item)

    # Sort by total descending
    income_items.sort(key=lambda x: x.total, reverse=True)
    expense_items.sort(key=lambda x: x.total, reverse=True)

    return CategoryBreakdown(
        income_categories=income_items,
        expense_categories=expense_items,
    )


def get_monthly_trends(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> MonthlyTrend:
    """
    Calculate monthly income, expenses, and net for trend visualization.
    """
    conditions = _date_filters(date_from, date_to)

    # Extract year and month, group by them
    year_col = extract("year", Transaction.date).label("year")
    month_col = extract("month", Transaction.date).label("month")

    query = db.query(
        year_col,
        month_col,
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)),
            0,
        ).label("income"),
        func.coalesce(
            func.sum(case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)),
            0,
        ).label("expenses"),
    ).group_by(year_col, month_col).order_by(year_col, month_col)

    if conditions:
        query = query.filter(and_(*conditions))

    rows = query.all()

    trends = []
    for row in rows:
        income = round(float(row.income), 2)
        expenses = round(float(row.expenses), 2)
        trends.append(
            MonthlyTrendItem(
                month=f"{int(row.year)}-{int(row.month):02d}",
                income=income,
                expenses=expenses,
                net=round(income - expenses, 2),
            )
        )

    return MonthlyTrend(trends=trends)


def get_recent_activity(db: Session, limit: int = 10) -> RecentActivity:
    """
    Get the most recent transactions.
    """
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )

    items = [
        RecentActivityItem(
            id=t.id,
            amount=t.amount,
            type=t.type.value,
            category=t.category,
            date=t.date,
            description=t.description,
        )
        for t in transactions
    ]

    return RecentActivity(transactions=items)


def get_dashboard_data(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> DashboardData:
    """
    Combined dashboard payload — calls all analytics functions
    and returns a single unified response.
    """
    return DashboardData(
        summary=get_financial_summary(db, date_from, date_to),
        category_breakdown=get_category_breakdown(db, date_from, date_to),
        monthly_trends=get_monthly_trends(db, date_from, date_to),
        recent_activity=get_recent_activity(db),
    )
