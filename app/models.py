from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, description="Natural language question about the data")
    max_rows: int = Field(default=100, ge=1, le=500)


class SQLGenerationResult(BaseModel):
    query: str = Field(..., description="The generated SELECT SQL statement")
    explanation: str = Field(..., description="Plain-English explanation of what the SQL does")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    assumptions: list[str] = Field(default_factory=list, description="Ambiguities the LLM resolved")


class AnalyticsResponse(BaseModel):
    sql_query: str
    result_data: list[dict]
    natural_language_answer: str
    key_insights: list[str]
    confidence: float
    retries_used: int = 0


class QueryError(BaseModel):
    error_type: str  # "validation_error" | "execution_error" | "llm_error"
    message: str
    failed_query: str | None = None


class HistoryEntry(BaseModel):
    question: str
    sql_query: str
    natural_language_answer: str
    confidence: float
    retries_used: int
