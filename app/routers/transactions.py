from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_viewer, require_analyst, require_admin
from app.models.user import User
from app.models.transaction import TransactionType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionFilter,
)
from app.services.transaction_service import (
    create_transaction,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    list_transactions,
    export_transactions_csv,
    export_transactions_json,
    import_transactions_csv,
    import_transactions_json,
)
from app.utils.exceptions import BadRequestException

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions",
    description="Retrieve transactions with optional filters and pagination.",
)
def list_transactions_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    type: Optional[TransactionType] = Query(None, description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date (inclusive)"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    search: Optional[str] = Query(None, max_length=100, description="Search in description"),
    current_user: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    filters = TransactionFilter(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
    )
    return list_transactions(db, filters, page=page, page_size=page_size)


@router.get(
    "/export",
    summary="Export transactions",
    description="Export filtered transactions as CSV or JSON.",
)
def export_transactions_endpoint(
    format: str = Query("csv", description="Export format: csv or json"),
    type: Optional[TransactionType] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
):
    filters = TransactionFilter(
        type=type, category=category, date_from=date_from,
        date_to=date_to, min_amount=min_amount, max_amount=max_amount,
    )

    if format.lower() == "csv":
        csv_content = export_transactions_csv(db, filters)
        return PlainTextResponse(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions.csv"},
        )
    elif format.lower() == "json":
        json_data = export_transactions_json(db, filters)
        return JSONResponse(content=json_data)
    else:
        raise BadRequestException("Format must be 'csv' or 'json'")


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get a transaction",
)
def get_transaction_endpoint(
    transaction_id: int,
    current_user: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    return get_transaction_by_id(db, transaction_id)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
    summary="Create a transaction",
)
def create_transaction_endpoint(
    data: TransactionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return create_transaction(db, data, user_id=current_user.id)


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update a transaction",
)
def update_transaction_endpoint(
    transaction_id: int,
    data: TransactionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return update_transaction(db, transaction_id, data)


@router.delete(
    "/{transaction_id}",
    status_code=204,
    summary="Delete a transaction",
)
def delete_transaction_endpoint(
    transaction_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    delete_transaction(db, transaction_id)
    return None


@router.post(
    "/import",
    summary="Import transactions",
    description="Import transactions from a CSV or JSON file.",
)
async def import_transactions_endpoint(
    file: UploadFile = File(..., description="CSV or JSON file to import"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    content = await file.read()
    content_str = content.decode("utf-8")

    if file.filename and file.filename.endswith(".json"):
        import json
        try:
            data = json.loads(content_str)
        except json.JSONDecodeError:
            raise BadRequestException("Invalid JSON file")
        count = import_transactions_json(db, data, user_id=current_user.id)
    elif file.filename and file.filename.endswith(".csv"):
        count = import_transactions_csv(db, content_str, user_id=current_user.id)
    else:
        raise BadRequestException("File must be .csv or .json")

    return {"message": f"Successfully imported {count} transactions", "count": count}
