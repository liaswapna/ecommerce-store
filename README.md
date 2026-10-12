# E-Commerce Store

A full-stack e-commerce platform built with FastAPI and React. Customers can browse products, add items to a cart, and place orders. Admins can create, edit and deactivate products. Customers can also search products in plain language ("something cozy for snow") with AI semantic search.

Built by **Swapna Lia Anil** · [github.com/liaswapna](https://github.com/liaswapna)

---

## Live Demo

- **Frontend:** https://fullstack-ecom-store.vercel.app
- **Backend API docs:** https://ecommerce-store-api-vgxw.onrender.com/docs

> Hosted on free tiers: the backend sleeps after 15 minutes idle, so the first request can take about a minute. After that it's fast.

---

## Tech Stack

**Backend**
- Python 3.12, FastAPI
- PostgreSQL + pgvector, SQLAlchemy, Alembic
- Gemini embeddings (`gemini-embedding-001`) for AI semantic search
- JWT authentication, bcrypt password hashing
- pytest (unit + integration tests)

**Frontend**
- React 19, TypeScript, Tailwind CSS
- Vite (dev), nginx (production)

**Infrastructure**
- Docker + Docker Compose (local)
- Neon (PostgreSQL + pgvector, production)
- Render (backend in Docker, production)
- Vercel (frontend, production)
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
- Order detail only returns the caller's own orders (404 otherwise), so users can't read each other's orders by changing the ID
- Admin dashboard: product list (including inactive), create/edit form with validation; lazy-loaded, protected in the UI (`AdminRoute`) and on the API (`require_admin`)
- AI semantic search with keyword fallback (see below)

---

## AI Semantic Search

Customers search by meaning, not exact words. "video calls from home" finds the webcam.

1. When an admin creates or edits a product, its name, description and category are turned into a 768-number embedding (Gemini `gemini-embedding-001`) and stored in a pgvector column. Edits only re-embed when the text changes.
2. A search embeds the query the same way and returns the 5 closest active products (cosine distance in Postgres; no separate vector database).
3. If there's no API key, Gemini fails, or nothing matches, it falls back to keyword search, so search always works. If embedding fails on save, the product still saves.

**Result:** on 15 hand-written test queries, the right product appeared in the first 3 results for **15/15** queries with semantic search vs **2/15** with keyword search (the app shows 5 results; the test checks the top 3, which is stricter). Run it yourself with `python -m scripts.evaluate_search`.

Tests never call Gemini: they use a fake embedder, so CI needs no API key.

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
│   │   ├── embedder.py          # Gemini embedder (AI search)
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
│   ├── scripts/
│   │   ├── seed.py              # Sample product data
│   │   ├── backfill_embeddings.py  # Fill in missing product embeddings
│   │   └── evaluate_search.py   # Keyword vs semantic hit rate
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── pages/               # Products, Cart, Orders, OrderDetail, Login, AdminProducts, AdminProductForm
│       ├── components/          # Navbar, AdminRoute
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
- PostgreSQL 16+ with the [pgvector](https://github.com/pgvector/pgvector) extension (macOS: `brew install pgvector`)

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
# GEMINI_API_KEY is optional — without it, search uses keyword matching

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
python -m scripts.seed

# Optional, needs GEMINI_API_KEY: embed existing products, then compare search quality
python -m scripts.backfill_embeddings
python -m scripts.evaluate_search
```

---

## Running with Docker

Runs the full stack (backend + frontend + database) in containers.

```bash
# Start everything
docker compose up --build

# Seed the database
docker compose exec backend python -m scripts.seed
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

116 tests (unit + integration). Tests run against a separate `ecommerce_store_test` database that is created fresh and wiped after every test. The main database is never touched.

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

1. **Test job** — spins up a Postgres container (with pgvector), installs dependencies, runs the full test suite
2. **deploy-backend** — triggers a Render redeploy (only if tests pass, only on push to main)
3. **deploy-frontend** — deploys to Vercel (only if tests pass, only on push to main)

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
| GET | `/products?page=&page_size=` | List active products (paginated) |
| GET | `/products/category/{category}` | Filter by category (paginated) |
| GET | `/products/search?q=` | AI semantic search, keyword fallback (top 5) |
| GET | `/products/{id}` | Get product by ID |

### Admin Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/products` | List all products, including inactive (paginated) |
| GET | `/admin/products/category/{category}` | Filter by category, including inactive |
| GET | `/admin/products/{id}` | Get any product by ID |
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
| DELETE | `/cart/clear` | Clear cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Place an order |
| GET | `/orders` | Order history |
| GET | `/orders/{id}` | Order detail (own orders only) |

---

## Environment Variables

### Backend

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `TEST_DATABASE_URL` | Test database connection string |
| `SECRET_KEY` | JWT signing secret — use a strong random value in production |
| `GEMINI_API_KEY` | Optional. Enables AI semantic search; without it, search uses keyword matching |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins (defaults to localhost; set to the Vercel URL in production) |

Generate a strong secret key:
```bash
openssl rand -hex 32
```

### Frontend

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (defaults to `http://localhost:8000`) |
