import os
import instructor
from groq import Groq
from dotenv import load_dotenv

from app.models import SQLGenerationResult, AnalyticsResponse
from app.prompt_builder import build_sql_generation_prompt, build_explanation_prompt

load_dotenv()

_client = instructor.from_groq(
    Groq(api_key=os.environ["GROQ_API_KEY"]),
    mode=instructor.Mode.JSON,
)

MODEL = "llama-3.3-70b-versatile"


def _create(response_model, prompt: str):
    return _client.chat.completions.create(
        model=MODEL,
        response_model=response_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )


def generate_sql(question: str) -> SQLGenerationResult:
    return _create(SQLGenerationResult, build_sql_generation_prompt(question))


def generate_sql_correction(question: str, failed_sql: str, error_message: str) -> SQLGenerationResult:
    from app.database import get_schema_text
    schema = get_schema_text()
    prompt = f"""The SQL query below was generated for the question but failed to execute. Fix it.

QUESTION: {question}

FAILED SQL:
{failed_sql}

EXECUTION ERROR:
{error_message}

DATABASE SCHEMA:
{schema}

RULES: Only return a corrected SELECT statement. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or GRANT."""
    return _create(SQLGenerationResult, prompt)


def generate_explanation(question: str, sql: str, results: list[dict]) -> AnalyticsResponse:
    return _create(AnalyticsResponse, build_explanation_prompt(question, sql, results))
