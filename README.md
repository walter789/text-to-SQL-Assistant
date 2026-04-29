# Text-to-SQL Analytics Assistant

A production-grade AI system that converts natural language questions into SQL queries, executes them against a relational database, and returns structured insights. All through a clean REST API and interactive UI.

---

## What It Does

Ask a question in plain English. Get back the SQL, the data, and a natural language explanation with key insights.

**Example:**
> *"Which product category had the highest total revenue?"*

Returns:
- The generated SQL query
- The query results as a table
- A plain-English answer with data-driven insights
- A confidence score

---

## System Architecture

```
User Question
     │
     ▼
┌─────────────┐
│ Streamlit UI│
└──────┬──────┘
       │ HTTP POST /query
       ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│                                             │
│  1. Schema Loader  ← SQLAlchemy metadata    │
│         │                                   │
│  2. Prompt Builder (schema + few-shot)      │
│         │                                   │
│  3. Groq LLM + instructor                   │
│         │  → SQLGenerationResult (Pydantic) │
│         │                                   │
│  4. SQL Validator  ← GUARDRAIL              │
│         │  blocks DELETE/DROP/INSERT etc.   │
│         │                                   │
│  5. SQL Executor (SQLAlchemy)               │
│         │  ── on error ──► Self-Correction  │
│         │                  (max 2 retries)  │
│  6. Result Explainer (Groq LLM)             │
│         │  → AnalyticsResponse (Pydantic)   │
└─────────────────────────────────────────────┘
       │
       ▼
  JSON Response
  { sql_query, result_data, answer, insights, confidence, retries_used }
```

---

## Key Engineering Decisions

### Structured Output via `instructor`
Instead of parsing raw LLM text, every LLM call returns a validated Pydantic V2 object. SQL generation returns a `SQLGenerationResult`, explanation returns an `AnalyticsResponse`. Zero string parsing, full type safety.

### SQL Safety Guardrail
A deterministic regex validator runs **before** any SQL touches the database. It blocks `DELETE`, `DROP`, `INSERT`, `UPDATE`, `TRUNCATE`, `ALTER`, `CREATE`, `GRANT`, and stacked queries (`;` injection). If triggered, the request is rejected immediately — the LLM never gets a second chance to cause damage.

### Schema-Aware Prompting
The LLM receives the full database schema (table names, column types, foreign keys) plus 3 sample rows per table and 2 few-shot examples before generating SQL. This grounds the model in the actual structure rather than guessing column names.

### Self-Correction Loop
If the generated SQL fails at execution, the error message is sent back to the LLM with the original question and failed query. It corrects itself and retries (max 2 attempts). The number of retries is surfaced in the API response for transparency.

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Structured Output | `instructor` + Pydantic V2 |
| API | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy Core |
| UI | Streamlit |
| Containerization | Docker + docker-compose |

---

## Project Structure

```
text-to-sql-assistant/
├── app/
│   ├── main.py           # FastAPI app — 4 endpoints
│   ├── models.py         # Pydantic V2 schemas
│   ├── database.py       # SQLAlchemy engine + schema introspection
│   ├── prompt_builder.py # Schema-aware prompt construction
│   ├── llm.py            # Groq + instructor integration
│   ├── validator.py      # SQL safety guardrail
│   └── executor.py       # SQL execution + self-correction loop
├── data/
│   └── seed.py           # Creates and seeds the Northwind SQLite database
├── ui/
│   └── app.py            # Streamlit dashboard
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query` | Main endpoint — NL question → SQL → insights |
| `GET` | `/schema` | Returns full DB schema with row counts |
| `GET` | `/history` | Last 20 queries and results |
| `GET` | `/health` | Health check |

**Request:**
```json
POST /query
{
  "question": "Which employee processed the most orders?",
  "max_rows": 100
}
```

**Response:**
```json
{
  "sql_query": "SELECT e.FirstName, e.LastName, COUNT(o.OrderID) ...",
  "result_data": [...],
  "natural_language_answer": "Nancy Davolio processed the most orders with 18 total.",
  "key_insights": ["Nancy Davolio leads with 18 orders", "..."],
  "confidence": 0.95,
  "retries_used": 0
}
```

---

## Dataset — Northwind

A classic relational dataset with 7 tables and realistic business data:

| Table | Description |
|---|---|
| `Customers` | 15 customers across 8 countries |
| `Orders` | 120 orders with dates and ship countries |
| `OrderDetails` | Line items with price, quantity, discount |
| `Products` | 20 products across 8 categories |
| `Categories` | Product categories |
| `Employees` | 9 sales employees |
| `Suppliers` | 8 suppliers across 5 countries |

---

## Setup & Run

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com) (no credit card required)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/text-to-sql-assistant.git
cd text-to-sql-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
 .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=gsk_...

# 4. Create and seed the database
python data/seed.py

# 5. Start the backend (Terminal 1)
uvicorn app.main:app --reload

# 6. Start the UI (Terminal 2)
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

Swagger docs available at `http://localhost:8000/docs`.

### Docker

```bash
# Add your key to .env first, then:
docker-compose up --build
```

---

## Example Queries to Try

- *"Which product category has the most products?"*
- *"Show me the top 5 customers by total order value"*
- *"What is the average order value per country?"*
- *"Which employee processed the most orders?"*
- *"List all discontinued products"*
- *"Which supplier provides the most expensive products on average?"*
