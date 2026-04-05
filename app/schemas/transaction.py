"""
Pydantic schemas for transaction-related requests and responses.
"""

from datetime import date as date_type
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.transaction import TransactionType


# ── Create / Update ──────────────────────────────────────
class TransactionCreate(BaseModel):
    """Payload for creating a financial record."""
    amount: float = Field(..., gt=0, examples=[1500.00])
    type: TransactionType = Field(..., examples=["income"])
    category: str = Field(..., min_length=1, max_length=50, examples=["Salary"])
    date: date_type = Field(..., examples=["2024-09-15"])
    description: Optional[str] = Field(
        None, max_length=500, examples=["Monthly salary from Acme Corp"]
    )

    model_config = {"populate_by_name": True}

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        """Round amount to 2 decimal places."""
        return round(v, 2)


class TransactionUpdate(BaseModel):
    """Payload for updating a financial record (all fields optional)."""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    date: Optional[date_type] = None
    description: Optional[str] = Field(None, max_length=500)

    model_config = {"populate_by_name": True}

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float | None) -> float | None:
        if v is not None:
            return round(v, 2)
        return v


# ── Response ─────────────────────────────────────────────
class TransactionResponse(BaseModel):
    """Full transaction record returned to the client."""
    id: int
    user_id: int
    amount: float
    type: TransactionType
    category: str
    date: date_type
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Filters (query parameters) ───────────────────────────
class TransactionFilter(BaseModel):
    """Query parameters for filtering transactions."""
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    search: Optional[str] = Field(None, max_length=100)

    model_config = {"populate_by_name": True}
