import re

DANGEROUS_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|REPLACE|MERGE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)

STACKED_QUERY = re.compile(r";\s*\S")  # semicolon followed by more content → stacked queries


class SQLValidationError(Exception):
    pass


def validate(sql: str) -> str:
    """
    Validate and clean an LLM-generated SQL string before execution.
    Returns the cleaned query on success, raises SQLValidationError on failure.
    """
    cleaned = sql.strip().rstrip(";").strip()

    if not cleaned:
        raise SQLValidationError("Empty SQL query.")

    match = DANGEROUS_KEYWORDS.search(cleaned)
    if match:
        raise SQLValidationError(
            f"Dangerous keyword '{match.group()}' detected. Only SELECT statements are permitted."
        )

    if STACKED_QUERY.search(cleaned):
        raise SQLValidationError("Stacked queries (multiple statements) are not permitted.")

    if not re.match(r"^\s*SELECT\b", cleaned, re.IGNORECASE):
        raise SQLValidationError("Only SELECT statements are allowed.")

    return cleaned
