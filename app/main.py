from collections import deque

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.models import QueryRequest, AnalyticsResponse, QueryError, HistoryEntry
from app.database import get_schema_dict
from app.llm import generate_sql, generate_explanation
from app.executor import run_with_self_correction
from app.validator import SQLValidationError

app = FastAPI(
    title="Text-to-SQL Analytics Assistant",
    description="Natural language → SQL → structured insights powered by Groq (Llama) + instructor",
    version="1.0.0",
)

_history: deque[HistoryEntry] = deque(maxlen=20)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/schema")
def schema():
    """Return the full database schema with table names, columns, types, and row counts."""
    return {"tables": get_schema_dict()}


@app.get("/history")
def history():
    """Return the last 20 queries and their results."""
    return {"history": list(_history)}


@app.post("/query", response_model=AnalyticsResponse)
def query(request: QueryRequest):
    """
    Main endpoint: accept a natural language question, generate SQL,
    validate it, execute it with self-correction, and return structured insights.
    """
    # Step 1: LLM generates SQL
    try:
        sql_result = generate_sql(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=QueryError(
            error_type="llm_error",
            message=f"SQL generation failed: {e}",
        ).model_dump())

    # Step 2: Execute with guardrail + self-correction loop
    try:
        rows, retries = run_with_self_correction(
            question=request.question,
            sql_result=sql_result,
            max_rows=request.max_rows,
        )
    except QueryError as e:
        raise HTTPException(status_code=422, detail=e.model_dump())

    # Step 3: LLM explains results and extracts insights
    try:
        response = generate_explanation(
            question=request.question,
            sql=sql_result.query,
            results=rows,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=QueryError(
            error_type="llm_error",
            message=f"Explanation generation failed: {e}",
        ).model_dump())

    response.sql_query = sql_result.query
    response.result_data = rows
    response.retries_used = retries

    _history.appendleft(HistoryEntry(
        question=request.question,
        sql_query=response.sql_query,
        natural_language_answer=response.natural_language_answer,
        confidence=response.confidence,
        retries_used=retries,
    ))

    return response
