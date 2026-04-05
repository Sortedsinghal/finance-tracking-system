import csv
import io
import json
import math
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilter,
    TransactionListResponse,
    TransactionResponse,
)
from app.utils.exceptions import NotFoundException, BadRequestException


def create_transaction(db: Session, data: TransactionCreate, user_id: int) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        description=data.description,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction_by_id(db: Session, transaction_id: int) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise NotFoundException(f"Transaction with id {transaction_id} not found")
    return transaction


def update_transaction(
    db: Session, transaction_id: int, data: TransactionUpdate
) -> Transaction:
    transaction = get_transaction_by_id(db, transaction_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> None:
    transaction = get_transaction_by_id(db, transaction_id)
    db.delete(transaction)
    db.commit()


def _apply_filters(query, filters: TransactionFilter):
    conditions = []

    if filters.type is not None:
        conditions.append(Transaction.type == filters.type)
    if filters.category is not None:
        conditions.append(Transaction.category == filters.category)
    if filters.date_from is not None:
        conditions.append(Transaction.date >= filters.date_from)
    if filters.date_to is not None:
        conditions.append(Transaction.date <= filters.date_to)
    if filters.min_amount is not None:
        conditions.append(Transaction.amount >= filters.min_amount)
    if filters.max_amount is not None:
        conditions.append(Transaction.amount <= filters.max_amount)
    if filters.search:
        conditions.append(Transaction.description.ilike(f"%{filters.search}%"))

    if conditions:
        query = query.filter(and_(*conditions))

    return query


def list_transactions(
    db: Session,
    filters: TransactionFilter,
    page: int = 1,
    page_size: int = 20,
) -> TransactionListResponse:
    query = db.query(Transaction)
    query = _apply_filters(query, filters)

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))

    transactions = (
        query.order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def export_transactions_csv(db: Session, filters: TransactionFilter) -> str:
    query = db.query(Transaction)
    query = _apply_filters(query, filters)
    transactions = query.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "amount", "type", "category", "date", "description"])

    for t in transactions:
        writer.writerow([t.id, t.amount, t.type.value, t.category, t.date.isoformat(), t.description or ""])

    return output.getvalue()


def export_transactions_json(db: Session, filters: TransactionFilter) -> list[dict]:
    query = db.query(Transaction)
    query = _apply_filters(query, filters)
    transactions = query.order_by(Transaction.date.desc()).all()

    return [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type.value,
            "category": t.category,
            "date": t.date.isoformat(),
            "description": t.description,
        }
        for t in transactions
    ]


def import_transactions_csv(db: Session, csv_content: str, user_id: int) -> int:
    reader = csv.DictReader(io.StringIO(csv_content))
    count = 0

    for row in reader:
        try:
            transaction = Transaction(
                user_id=user_id,
                amount=round(float(row["amount"]), 2),
                type=TransactionType(row["type"]),
                category=row["category"],
                date=date.fromisoformat(row["date"]),
                description=row.get("description") or None,
            )
            db.add(transaction)
            count += 1
        except (ValueError, KeyError) as e:
            raise BadRequestException(f"Invalid row in CSV: {e}")

    db.commit()
    return count


def import_transactions_json(db: Session, data: list[dict], user_id: int) -> int:
    count = 0

    for item in data:
        try:
            transaction = Transaction(
                user_id=user_id,
                amount=round(float(item["amount"]), 2),
                type=TransactionType(item["type"]),
                category=item["category"],
                date=date.fromisoformat(item["date"]),
                description=item.get("description"),
            )
            db.add(transaction)
            count += 1
        except (ValueError, KeyError) as e:
            raise BadRequestException(f"Invalid record in JSON: {e}")

    db.commit()
    return count
