# onlyproducts
It's a product and Services application 
# 🛒 AI-Powered E-Commerce Platform

A dual-service FastAPI backend with an AI chat assistant powered by **Groq + LLaMA 3.5**, connected to a **Lovable**-hosted React frontend.

---

## 📁 Project Structure

```
project/
├── main.py                  # Entry point — starts both FastAPI apps
├── db.py                    # Shared run_query() database helper
├── Services/
│   └── query.py             # users, orders, checking_out, create_user
├── product/
│   └── query.py             # get_all_products, create_product, reserve/release, search, recommendations
├── chat/
│   └── query.py             # chat_with_groq() — Groq API integration
└── docs/
    └── architecture.docx    # Full technical design document
```

---

## ⚙️ Prerequisites

- Python 3.10+
- PostgreSQL (running locally or remote)
- A [Groq API key](https://console.groq.com/) (free tier works)

---

## 🚀 Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn psycopg2-binary groq pydantic
```

### 4. Set environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=your_db_user
DB_PASSWORD=your_db_password
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **Never commit your `.env` file.** Add it to `.gitignore`.

### 5. Set up the database

Run the following SQL to create the required tables:

```sql
CREATE TABLE users (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    balance NUMERIC(10, 2) DEFAULT 0
);

CREATE TABLE products (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(200) NOT NULL,
    price    NUMERIC(10, 2) NOT NULL,
    stock    INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(100)
);

CREATE TABLE orders (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    status     VARCHAR(50) DEFAULT 'pending',
    total      NUMERIC(10, 2)
);

CREATE TABLE chat_history (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    query      TEXT,
    response   TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Run the app

```bash
python main.py
```

This starts two servers simultaneously:

| Service  | URL                        |
|----------|----------------------------|
| Services | http://localhost:9000      |
| Products | http://localhost:9001      |

---

## 📡 API Reference

### Services API — Port 9000

| Method | Endpoint       | Description                                      |
|--------|----------------|--------------------------------------------------|
| GET    | `/users`       | List all users                                   |
| GET    | `/orders`      | List all orders (id, user_id, status, total)     |
| POST   | `/checkout`    | Checkout — body: `{user_id, product_id, quantity}` |
| POST   | `/new_user`    | Create a user — params: `?name=&balance=`        |

**Checkout request body:**
```json
{
  "user_id": 1,
  "product_id": 3,
  "quantity": 2
}
```

---

### Products API — Port 9001

| Method | Endpoint                         | Description                                   |
|--------|----------------------------------|-----------------------------------------------|
| GET    | `/products`                      | List all products                             |
| GET    | `/products/{id}`                 | Get product by ID (404 if not found)          |
| POST   | `/products`                      | Create a product                              |
| PATCH  | `/products/{id}/reserve`         | Reserve stock (409 if out of stock)           |
| PATCH  | `/products/{id}/release`         | Release (restore) stock                      |
| GET    | `/search?query=`                 | Keyword search + category recommendations     |
| GET    | `/chat?query=&user_id=`          | AI chat assistant (Groq / LLaMA 3.5)          |
| GET    | `/chat/history?user_id=`         | Fetch chat history (per-user or global)       |

**Create product request body:**
```json
{
  "name": "Wireless Headphones",
  "price": 49.99,
  "stock": 100,
  "category": "Electronics"
}
```

**Chat response example:**
```json
{
  "success": true,
  "query": "show me budget headphones",
  "response": "Here are some great budget options...",
  "search_results": [...],
  "recommendations": [...],
  "source": "groq",
  "from_history": false
}
```

---

## 🤖 AI Chat (Groq + LLaMA 3.5)

The `/chat` endpoint:
1. Checks `chat_history` for a recent matching answer first.
2. If no cache hit, enriches the prompt with live product data.
3. Calls **Groq API** using the **LLaMA 3.5** model.
4. Saves the response to `chat_history` for future reuse.

Make sure `GROQ_API_KEY` is set in your environment before running.

---

## 🌐 Frontend (Lovable)

The frontend is built and hosted on [Lovable](https://lovable.dev).  
Both APIs are configured with CORS to accept all origins during development:

```python
origins = ["*"]  # ⚠️ Change this before going to production
```

**Before deploying to production**, lock this down:
```python
origins = ["https://your-app-name.lovable.app"]
```

---

## 🔍 Auto-generated API Docs

FastAPI generates interactive Swagger docs automatically:

- Services API → http://localhost:9000/docs
- Products API → http://localhost:9001/docs

---

## ⚠️ Known Limitations (v1)

- No authentication — `user_id` is a plain query param
- Threading model — both apps share one process; use separate processes in production
- `origins = ["*"]` — must be scoped before go-live
- No rate limiting on `/chat` (Groq free tier has RPM caps)
- Stock reserve has no row-level DB lock — may oversell under high concurrency

---

## 🗺️ Roadmap

- [ ] JWT authentication on checkout and user creation
- [ ] Docker Compose for isolated service processes
- [ ] Scoped CORS for Lovable production domain
- [ ] `SELECT FOR UPDATE` on stock reservation
- [ ] Semantic search with pgvector
- [ ] Prometheus metrics + Grafana dashboard
- [ ] Streaming responses on `/chat`

---

## 📄 License

MIT — feel free to use and extend.
