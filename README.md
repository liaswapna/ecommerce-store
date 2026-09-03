# E-Commerce Store

A full-stack e-commerce platform built with FastAPI and React. Customers can browse products, manage a cart, and place orders. Admins can manage products and view orders.

---

## Live Demo

- **Frontend:** coming soon
- **Backend API:** coming soon

---

## Tech Stack

**Backend**
- Python 3.12, FastAPI
- PostgreSQL, SQLAlchemy, Alembic
- JWT authentication, bcrypt password hashing
- pytest (unit + integration tests)

**Frontend**
- React 18, TypeScript, Tailwind CSS
- Vite (dev), nginx (production)

**Infrastructure**
- Docker + Docker Compose (local)
- Neon (PostgreSQL, production) (TODO)
- Render (backend, production) (TODO)
- Vercel (frontend, production) (TODO)
- GitHub Actions (CI/CD)

---

## Architecture

```
Request → Route → Service → Repository → Database
```

- **Routes** — HTTP handlers, no business logic
- **Services** — business logic, no HTTP concerns
- **Repositories** — all database queries in one place
- **Models** — SQLAlchemy table definitions
- **Schemas** — Pydantic request/response shapes

---

## Features

- JWT authentication (register, login, protected routes)
- Product catalog with category filtering and pagination
- Shopping cart with stock validation
- Order placement with atomic transactions (check stock → decrement → create order → clear cart)
- Admin routes for product management
- Soft delete on products (preserves order history integrity)
- Prices stored as `NUMERIC(10,2)` — no floating point errors on money
- Price and name snapshotted on `OrderItem` — historical accuracy even if product changes

---

## Project Structure

```
ecommerce-store/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, Alembic migration on startup
│   │   ├── config.py            # Settings via pydantic-settings, reads .env
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── dependencies.py      # get_current_user, require_admin
│   │   ├── exceptions.py        # NotFoundError, DatabaseError, OutOfStockError
│   │   ├── models/              # SQLAlchemy table definitions
│   │   ├── schemas/             # Pydantic request/response shapes
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── repositories/        # Database queries
│   ├── migrations/              # Alembic migration files
│   ├── tests/
│   │   ├── conftest.py          # Test client, test DB setup
│   │   ├── unit/                # Isolated tests with mocked repositories
│   │   └── integration/         # Full request → DB tests
│   ├── seed.py                  # Sample product data
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── pages/               # ProductsPage, CartPage, OrdersPage, OrderDetailPage, LoginPage
│       ├── context/             # AuthContext (JWT token state)
│       └── api.ts               # All API calls in one place
├── .github/
│   └── workflows/
│       └── ci.yml               # Run tests → deploy on pass
├── backend/Dockerfile
├── frontend/Dockerfile
└── docker-compose.yml
```

---

## Local Development

### Prerequisites

- Python 3.12
- Node.js 20
- PostgreSQL 16+

### Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local database URLs and a secret key

# Create the databases
psql -c "CREATE DATABASE ecommerce_store;"
psql -c "CREATE DATABASE ecommerce_store_test;"

# Start the backend (migrations run automatically on startup)
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

### Seed sample data

```bash
cd backend
source venv/bin/activate
python seed.py
```

---

## Running with Docker

Runs the full stack (backend + frontend + database) in containers.

```bash
# Start everything
docker compose up --build

# Seed the database
docker compose exec backend python seed.py
```

- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`

```bash
# Stop containers (keeps data)
docker compose stop

# Stop and wipe all data
docker compose down -v
```

> **Note:** Set `SECRET_KEY` as an environment variable on your machine before running Docker:
> ```bash
> export SECRET_KEY=your-secret-key-here
> docker compose up --build
> ```

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

Tests run against a separate `ecommerce_store_test` database that is created fresh and wiped after every test. The main database is never touched.

```bash
# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## CI/CD Pipeline

GitHub Actions runs on every push and pull request to `main`:

1. **Test job** — spins up a Postgres container, installs dependencies, runs the full test suite
2. **deploy-backend** — triggers a Render redeploy (only if tests pass, only on push to main) (TODO)
3. **deploy-frontend** — deploys to Vercel (only if tests pass, only on push to main) (TODO)

Pull requests run tests but never deploy. Branch protection on `main` blocks merging until the `test` job passes.

All secrets (database URLs, API keys) are stored in GitHub Secrets — never in code.

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns JWT token |
| GET | `/auth/me` | Get current user |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all active products |
| GET | `/products/{id}` | Get product by ID |
| GET | `/products/category/{category}` | Filter by category |

### Admin Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/products` | Create product |
| PUT | `/admin/products/{id}` | Update product |
| DELETE | `/admin/products/{id}` | Soft delete product |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart` | Get cart with product details |
| POST | `/cart` | Add item to cart |
| PATCH | `/cart` | Update item quantity |
| DELETE | `/cart/{product_id}` | Remove item |
| DELETE | `/cart` | Clear cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Place an order |
| GET | `/orders` | Order history |
| GET | `/orders/{id}` | Order detail |

---

## Environment Variables

### Backend

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `TEST_DATABASE_URL` | Test database connection string |
| `SECRET_KEY` | JWT signing secret — use a strong random value in production |

Generate a strong secret key:
```bash
openssl rand -hex 32
```

### Frontend

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (defaults to `http://localhost:8000`) |
