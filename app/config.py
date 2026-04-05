"""
Application configuration — loads settings from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration class for the application."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = os.getenv("APP_NAME", "Finance Tracker")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

    # ── JWT / Auth ───────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # ── Pagination ───────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── Predefined categories ────────────────────────────
    INCOME_CATEGORIES: list[str] = [
        "Salary",
        "Freelance",
        "Investment",
        "Business",
        "Rental",
        "Refund",
        "Other Income",
    ]

    EXPENSE_CATEGORIES: list[str] = [
        "Rent",
        "Groceries",
        "Utilities",
        "Transport",
        "Healthcare",
        "Entertainment",
        "Education",
        "Shopping",
        "Dining",
        "Insurance",
        "Subscriptions",
        "Other Expense",
    ]


settings = Settings()
