"""
Database seeder — populates the database with demo users and transactions.

Usage:
    python -m app.seed
"""

import random
from datetime import date, timedelta

from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.utils.security import hash_password


def seed_database():
    """Create tables and insert demo data."""

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Skip if data already exists
        if db.query(User).count() > 0:
            print("⚠  Database already contains data. Skipping seed.")
            return

        print("🌱 Seeding database...")

        # ── Users ────────────────────────────────────────
        users = [
            User(
                username="admin",
                email="admin@financetracker.com",
                hashed_password=hash_password("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
            ),
            User(
                username="analyst",
                email="analyst@financetracker.com",
                hashed_password=hash_password("analyst123"),
                full_name="Sarah Analyst",
                role=UserRole.ANALYST,
            ),
            User(
                username="viewer",
                email="viewer@financetracker.com",
                hashed_password=hash_password("viewer123"),
                full_name="Alex Viewer",
                role=UserRole.VIEWER,
            ),
        ]

        for user in users:
            db.add(user)
        db.flush()

        print(f"   ✓ Created {len(users)} users")

        # ── Transactions ─────────────────────────────────
        income_entries = [
            ("Salary", 5000.00, "Monthly salary"),
            ("Salary", 5000.00, "Monthly salary"),
            ("Salary", 5000.00, "Monthly salary"),
            ("Salary", 5000.00, "Monthly salary"),
            ("Salary", 5000.00, "Monthly salary"),
            ("Salary", 5200.00, "Monthly salary — with raise"),
            ("Freelance", 1200.00, "Website redesign project"),
            ("Freelance", 800.00, "Logo design for startup"),
            ("Freelance", 1500.00, "Mobile app consulting"),
            ("Freelance", 950.00, "Content writing project"),
            ("Investment", 320.00, "Stock dividends Q1"),
            ("Investment", 450.00, "Stock dividends Q2"),
            ("Investment", 280.00, "Mutual fund returns"),
            ("Rental", 1800.00, "Property rental income"),
            ("Rental", 1800.00, "Property rental income"),
            ("Rental", 1800.00, "Property rental income"),
            ("Refund", 149.99, "Electronics return refund"),
            ("Refund", 45.00, "Subscription cancellation refund"),
            ("Other Income", 200.00, "Sold old furniture"),
            ("Business", 3500.00, "Consulting project payment"),
        ]

        expense_entries = [
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Rent", 1500.00, "Monthly apartment rent"),
            ("Groceries", 285.50, "Weekly grocery shopping"),
            ("Groceries", 312.75, "Weekly grocery shopping"),
            ("Groceries", 198.30, "Mid-week grocery run"),
            ("Groceries", 425.00, "Monthly bulk grocery shopping"),
            ("Groceries", 156.80, "Quick grocery pickup"),
            ("Utilities", 120.00, "Electricity bill"),
            ("Utilities", 45.00, "Internet service"),
            ("Utilities", 65.00, "Water and sewage"),
            ("Utilities", 85.00, "Gas bill"),
            ("Transport", 150.00, "Monthly metro pass"),
            ("Transport", 45.00, "Uber rides"),
            ("Transport", 62.50, "Gas for car"),
            ("Healthcare", 250.00, "Doctor visit and medication"),
            ("Healthcare", 85.00, "Pharmacy — prescriptions"),
            ("Entertainment", 15.99, "Netflix subscription"),
            ("Entertainment", 12.99, "Spotify subscription"),
            ("Entertainment", 55.00, "Movie tickets and dinner"),
            ("Entertainment", 120.00, "Concert tickets"),
            ("Education", 299.00, "Online course — Python advanced"),
            ("Education", 49.99, "Technical book purchase"),
            ("Shopping", 189.99, "New running shoes"),
            ("Shopping", 79.99, "Clothing purchase"),
            ("Dining", 42.50, "Dinner at Italian restaurant"),
            ("Dining", 28.00, "Lunch with colleagues"),
            ("Dining", 65.00, "Birthday dinner celebration"),
            ("Insurance", 200.00, "Health insurance premium"),
            ("Insurance", 150.00, "Car insurance monthly"),
            ("Subscriptions", 9.99, "Cloud storage"),
            ("Subscriptions", 14.99, "News subscription"),
        ]

        # Spread transactions over 6 months
        today = date.today()
        start_date = today - timedelta(days=180)

        admin_user = users[0]
        transaction_objects = []

        # Create income transactions spread across months
        for i, (category, amount, desc) in enumerate(income_entries):
            days_offset = int((i / len(income_entries)) * 180)
            txn_date = start_date + timedelta(days=days_offset)

            transaction_objects.append(
                Transaction(
                    user_id=admin_user.id,
                    amount=amount,
                    type=TransactionType.INCOME,
                    category=category,
                    date=txn_date,
                    description=desc,
                )
            )

        # Create expense transactions spread across months
        for i, (category, amount, desc) in enumerate(expense_entries):
            days_offset = int((i / len(expense_entries)) * 180)
            txn_date = start_date + timedelta(days=days_offset)

            transaction_objects.append(
                Transaction(
                    user_id=admin_user.id,
                    amount=amount,
                    type=TransactionType.EXPENSE,
                    category=category,
                    date=txn_date,
                    description=desc,
                )
            )

        for txn in transaction_objects:
            db.add(txn)

        db.commit()
        print(f"   ✓ Created {len(transaction_objects)} transactions")
        print()
        print("🎉 Seeding complete!")
        print()
        print("   Demo credentials:")
        print("   ┌──────────┬─────────────┬─────────┐")
        print("   │ Username │ Password    │ Role    │")
        print("   ├──────────┼─────────────┼─────────┤")
        print("   │ admin    │ admin123    │ Admin   │")
        print("   │ analyst  │ analyst123  │ Analyst │")
        print("   │ viewer   │ viewer123   │ Viewer  │")
        print("   └──────────┴─────────────┴─────────┘")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
