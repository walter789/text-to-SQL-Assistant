from sqlalchemy import text

from app.database import engine
from app.validator import validate, SQLValidationError
from app.models import SQLGenerationResult, AnalyticsResponse, QueryError

MAX_RETRIES = 2


def execute_query(sql: str, max_rows: int = 100) -> list[dict]:
    """Execute a validated SELECT and return rows as a list of dicts."""
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        keys = list(result.keys())
        rows = result.fetchmany(max_rows)
        return [dict(zip(keys, row)) for row in rows]


def run_with_self_correction(
    question: str,
    sql_result: SQLGenerationResult,
    max_rows: int,
) -> tuple[list[dict], int]:
    """
    Attempt SQL execution. On failure, ask the LLM to correct the query.
    Returns (rows, retries_used). Raises QueryError after MAX_RETRIES.
    """
    from app.llm import generate_sql_correction

    current_sql_result = sql_result
    retries = 0

    while retries <= MAX_RETRIES:
        try:
            cleaned = validate(current_sql_result.query)
            rows = execute_query(cleaned, max_rows)
            return rows, retries
        except SQLValidationError as e:
            raise QueryError(
                error_type="validation_error",
                message=str(e),
                failed_query=current_sql_result.query,
            )
        except Exception as e:
            if retries == MAX_RETRIES:
                raise QueryError(
                    error_type="execution_error",
                    message=f"Query failed after {MAX_RETRIES} correction attempts: {e}",
                    failed_query=current_sql_result.query,
                )
            retries += 1
            current_sql_result = generate_sql_correction(
                question=question,
                failed_sql=current_sql_result.query,
                error_message=str(e),
            )

    raise QueryError(error_type="execution_error", message="Unexpected exit from retry loop.")
