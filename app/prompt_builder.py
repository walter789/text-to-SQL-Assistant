from app.database import get_schema_text

FEW_SHOT_EXAMPLES = """
Example 1:
Question: "What are the top 3 best-selling products by total quantity sold?"
SQL:
SELECT p.ProductName, SUM(od.Quantity) AS total_qty
FROM OrderDetails od
JOIN Products p ON od.ProductID = p.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY total_qty DESC
LIMIT 3;

Example 2:
Question: "Which country do most of our customers come from?"
SQL:
SELECT Country, COUNT(*) AS customer_count
FROM Customers
GROUP BY Country
ORDER BY customer_count DESC
LIMIT 1;
""".strip()


def build_sql_generation_prompt(question: str) -> str:
    schema = get_schema_text()
    return f"""You are an expert SQL analyst. Your job is to convert a natural language question into a valid SQLite SELECT query.

DATABASE SCHEMA:
{schema}

FEW-SHOT EXAMPLES:
{FEW_SHOT_EXAMPLES}

STRICT RULES:
- Only generate SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or GRANT.
- Use table and column names exactly as shown in the schema above.
- Always use JOINs when data from multiple tables is needed.
- Add LIMIT if the result could return many rows (default LIMIT 100).
- If the question is ambiguous, state your assumption in the assumptions field.

QUESTION: {question}

Return a SQLGenerationResult with the SQL query, a plain-English explanation of what it does, a confidence score (0.0-1.0), and any assumptions you made."""


def build_explanation_prompt(question: str, sql: str, results: list[dict]) -> str:
    result_preview = str(results[:10]) if results else "No rows returned."
    return f"""You are an expert data analyst. A user asked a question about business data and we retrieved results from a database.

ORIGINAL QUESTION: {question}

SQL QUERY EXECUTED:
{sql}

QUERY RESULTS (up to 10 rows shown):
{result_preview}

Total rows returned: {len(results)}

Your task:
1. Write a clear, concise natural_language_answer (2-4 sentences) directly answering the user's question using the actual data.
2. List 2-4 key_insights — specific, data-driven observations from the results (e.g. "Product X accounts for 34% of total revenue").
3. Set confidence (0.0-1.0) based on how completely the data answers the question.

Be specific — always reference actual values from the results, not generic statements."""
