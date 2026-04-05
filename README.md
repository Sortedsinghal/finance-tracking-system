# 💰 Finance Tracker — Python Finance System Backend

A full-stack **Python-powered finance tracking system** built with **FastAPI**, **SQLAlchemy**, and **SQLite**, featuring JWT authentication, role-based access control, and a premium dark-themed dashboard UI.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)

---

## ✨ Features

### Core
- **Financial Records Management** — Full CRUD for income and expense records
- **Filtering & Pagination** — Filter by type, category, date range, amount range, and text search
- **Analytics & Summaries** — Total income/expenses, balance, category breakdown, monthly trends
- **Role-Based Access Control** — Three tiers: Viewer, Analyst, Admin
- **JWT Authentication** — Secure token-based auth with bcrypt password hashing

### Frontend Dashboard
- **Premium Dark Theme** — Glassmorphism UI with smooth animations
- **Interactive Charts** — Monthly trends (bar+line) and category breakdown (doughnut) via Chart.js
- **Responsive Design** — Works on desktop and tablet
- **Role-Aware UI** — Controls dynamically shown/hidden based on user permissions

### Additional
- **CSV/JSON Export** — Download filtered transaction data
- **CSV/JSON Import** — Bulk upload financial records
- **API Documentation** — Auto-generated Swagger (OpenAPI) and ReDoc
- **Unit Tests** — Comprehensive test suite with pytest
- **Seed Data** — Pre-populated demo data for immediate testing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Static)                       │
│              HTML / CSS / JS  +  Chart.js                   │
├─────────────────────────────────────────────────────────────┤
│                     FastAPI Backend                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Routes   │  │ Schemas  │  │ Services │  │   Auth   │   │
│  │ (API)     │→ │(Pydantic)│→ │(Business │→ │(JWT+RBAC)│   │
│  │          │  │          │  │  Logic)  │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                │
│         SQLAlchemy ORM  →  SQLite Database                   │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
assignment/
├── app/                         # Application package
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from environment
│   ├── database.py              # SQLAlchemy engine & session
│   ├── seed.py                  # Demo data seeder
│   ├── models/                  # ORM models
│   │   ├── user.py              # User with role enum
│   │   └── transaction.py       # Financial records
│   ├── schemas/                 # Pydantic validation
│   │   ├── user.py              # User request/response
│   │   ├── transaction.py       # Transaction request/response
│   │   └── analytics.py         # Analytics responses
│   ├── routers/                 # API endpoints
│   │   ├── auth.py              # Login, register, profile
│   │   ├── users.py             # User management (admin)
│   │   ├── transactions.py      # CRUD + filters + import/export
│   │   └── analytics.py         # Summaries, breakdowns, trends
│   ├── services/                # Business logic
│   │   ├── auth_service.py      # Auth operations
│   │   ├── user_service.py      # User CRUD
│   │   ├── transaction_service.py # Transaction operations
│   │   └── analytics_service.py # Summary computations
│   ├── middleware/
│   │   └── auth.py              # JWT verification & RBAC
│   └── utils/
│       ├── security.py          # Password hashing, JWT helpers
│       └── exceptions.py        # Custom HTTP exceptions
├── static/                      # Frontend assets
│   ├── login.html               # Login page
│   ├── index.html               # Dashboard SPA
│   ├── css/style.css            # Complete stylesheet
│   └── js/
│       ├── api.js               # HTTP client
│       ├── auth.js              # Auth state management
│       ├── app.js               # Main app logic
│       └── charts.js            # Chart.js rendering
├── tests/                       # Test suite
│   ├── conftest.py              # Fixtures & helpers
│   ├── test_auth.py
│   ├── test_transactions.py
│   ├── test_analytics.py
│   └── test_users.py
├── requirements.txt
├── run.py                       # Start script
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** installed

### 1. Clone & setup

```bash
cd assignment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for development)
```

### 3. Seed demo data

```bash
python -m app.seed
```

This creates 3 users and ~55 financial transactions across 6 months.

### 4. Start the server

```bash
python run.py
```

Or run directly with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open in browser

| URL | Description |
|-----|-------------|
| [http://localhost:8000](http://localhost:8000) | Login Page |
| [http://localhost:8000/dashboard](http://localhost:8000/dashboard) | Dashboard |
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger API Docs |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc API Docs |

---

## 🔐 Demo Credentials

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full access — CRUD transactions, manage users |
| `analyst` | `analyst123` | Analyst | View records, apply filters, access analytics, export data |
| `viewer` | `viewer123` | Viewer | View financial summaries and recent activity |

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `GET` | `/api/auth/me` | Get current user profile |

### Transactions
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/transactions` | Viewer+ | List with filters & pagination |
| `GET` | `/api/transactions/{id}` | Viewer+ | Get single record |
| `POST` | `/api/transactions` | Admin | Create new record |
| `PUT` | `/api/transactions/{id}` | Admin | Update existing record |
| `DELETE` | `/api/transactions/{id}` | Admin | Delete record |
| `GET` | `/api/transactions/export` | Analyst+ | Export as CSV/JSON |
| `POST` | `/api/transactions/import` | Admin | Import from CSV/JSON |

### Analytics
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/analytics/summary` | Viewer+ | Total income, expenses, balance |
| `GET` | `/api/analytics/categories` | Analyst+ | Category breakdown |
| `GET` | `/api/analytics/monthly` | Analyst+ | Monthly income vs expense trends |
| `GET` | `/api/analytics/recent` | Viewer+ | Recent transactions |
| `GET` | `/api/analytics/dashboard` | Viewer+ | Combined dashboard payload |

### User Management
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users` | Admin | List all users |
| `GET` | `/api/users/{id}` | Admin | Get user details |
| `PUT` | `/api/users/{id}` | Admin | Update user role/status |
| `DELETE` | `/api/users/{id}` | Admin | Deactivate user (soft-delete) |

### Example: Login & Create Transaction

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create a transaction
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 3500.00,
    "type": "income",
    "category": "Freelance",
    "date": "2024-09-20",
    "description": "Web design project"
  }'
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 🏛️ Design Decisions & Assumptions

### Architecture
- **Service Layer Pattern** — Business logic is separated from route handlers into dedicated service modules, making the code testable and maintainable.
- **Dependency Injection** — FastAPI's `Depends()` is used throughout for database sessions, auth verification, and role checking.
- **Pydantic Validation** — All request/response data is validated through Pydantic schemas with strict type checking.

### Security
- **JWT Tokens** — Stateless authentication using signed JWT tokens with configurable expiry.
- **bcrypt Hashing** — Passwords are never stored in plain text; bcrypt provides adaptive hashing.
- **Role Hierarchy** — Admin > Analyst > Viewer. Higher roles inherit all permissions of lower roles.

### Data Model
- **Soft Deletion for Users** — Users are deactivated rather than deleted to preserve referential integrity.
- **Predefined Categories** — A sensible set of income and expense categories is provided, but the API accepts any string value for flexibility.
- **Float for Amounts** — Amounts are stored as floats rounded to 2 decimal places. For a production finance system, `Decimal` or integer cents would be preferred.

### Frontend
- **Server-Rendered HTML** — Login and dashboard pages are served as static files by FastAPI, avoiding the complexity of a separate build tool.
- **Chart.js CDN** — Charts are rendered client-side using Chart.js loaded from a CDN.
- **Role-Aware UI** — DOM elements with `data-role` attributes are hidden for users who lack the required role level.

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115 |
| Language | Python 3.10+ |
| Database | SQLite (via SQLAlchemy 2.0) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Testing | pytest |
| Frontend | Vanilla HTML/CSS/JS + Chart.js |
| API Docs | Swagger UI + ReDoc (auto-generated) |

