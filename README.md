# Finance Tracker

A finance tracking system built with FastAPI, SQLAlchemy, and SQLite. Includes JWT auth, role-based access control, and a dashboard UI.

## Features

- CRUD for income and expense records
- Filtering by type, category, date range, amount, and text search
- Analytics: total income/expenses, balance, category breakdown, monthly trends
- Three-tier RBAC: Viewer, Analyst, Admin
- JWT authentication with bcrypt password hashing
- CSV/JSON import and export
- Interactive charts (Chart.js) and a dark-themed dashboard
- Auto-generated API docs (Swagger + ReDoc)
- Test suite with pytest (42 tests)

## Project Structure

```
app/
├── main.py               # FastAPI app setup
├── config.py             # Env-based settings
├── database.py           # SQLAlchemy engine/session
├── seed.py               # Demo data
├── models/               # ORM models (User, Transaction)
├── schemas/              # Pydantic request/response schemas
├── routers/              # API endpoints
├── services/             # Business logic
├── middleware/            # JWT verification, RBAC
└── utils/                # Password hashing, JWT helpers, exceptions
static/                   # Frontend (HTML/CSS/JS)
tests/                    # pytest test suite
```

## Setup

```bash
# Clone and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (Optional) configure
cp .env.example .env

# Start the server (creates DB + seeds demo data on first run)
python run.py
```

The server starts at http://localhost:8000

| URL | What |
|-----|------|
| `/` | Login page |
| `/dashboard` | Dashboard |
| `/docs` | Swagger API docs |
| `/redoc` | ReDoc |

## Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin (full access) |
| analyst | analyst123 | Analyst (view + analytics + export) |
| viewer | viewer123 | Viewer (read-only) |

## API Endpoints

### Auth
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Get JWT token
- `GET /api/auth/me` — Current user profile

### Transactions
- `GET /api/transactions` — List with filters and pagination (Viewer+)
- `GET /api/transactions/{id}` — Get single record (Viewer+)
- `POST /api/transactions` — Create record (Admin)
- `PUT /api/transactions/{id}` — Update record (Admin)
- `DELETE /api/transactions/{id}` — Delete record (Admin)
- `GET /api/transactions/export?format=csv` — Export (Analyst+)
- `POST /api/transactions/import` — Import CSV/JSON (Admin)

### Analytics
- `GET /api/analytics/summary` — Income, expenses, balance (Viewer+)
- `GET /api/analytics/categories` — Category breakdown (Analyst+)
- `GET /api/analytics/monthly` — Monthly trends (Analyst+)
- `GET /api/analytics/recent` — Recent activity (Viewer+)
- `GET /api/analytics/dashboard` — Combined payload (Viewer+)

### Users (Admin only)
- `GET /api/users` — List users
- `GET /api/users/{id}` — User details
- `PUT /api/users/{id}` — Update role/status
- `DELETE /api/users/{id}` — Deactivate user

## Running Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Design Decisions

- **Service layer** — Business logic is in `services/`, separate from route handlers. Easier to test and refactor.
- **Dependency injection** — FastAPI's `Depends()` handles DB sessions and auth checks.
- **Role hierarchy** — Admin > Analyst > Viewer. Higher roles inherit lower role permissions.
- **Soft delete for users** — Users are deactivated instead of deleted to keep referential integrity.
- **Float for amounts** — Stored as float rounded to 2 decimal places. A production system would use `Decimal` or integer cents.
- **SQLite** — Chose for zero-config setup. The ORM abstraction means switching to Postgres is just a connection string change.

## Tech Stack

| | |
|---|---|
| Framework | FastAPI |
| Database | SQLite + SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Tests | pytest |
| Frontend | HTML/CSS/JS + Chart.js |
