import os
from sqlalchemy import create_engine, text, inspect

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "northwind.db")
DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_schema_text() -> str:
    """Return a prompt-ready description of every table: columns, types, FKs, sample rows."""
    inspector = inspect(engine)
    lines = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        fks = inspector.get_foreign_keys(table_name)

        col_defs = []
        for col in columns:
            col_type = str(col["type"])
            pk_flag = " (PK)" if col.get("primary_key") else ""
            col_defs.append(f"  {col['name']} {col_type}{pk_flag}")

        fk_notes = []
        for fk in fks:
            fk_notes.append(
                f"  FK: {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}"
            )

        lines.append(f"Table: {table_name}")
        lines.append("Columns:")
        lines.extend(col_defs)
        if fk_notes:
            lines.append("Foreign Keys:")
            lines.extend(fk_notes)

        with engine.connect() as conn:
            rows = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3")).fetchall()
            col_names = [c["name"] for c in columns]
            if rows:
                lines.append("Sample rows (3):")
                lines.append("  " + " | ".join(col_names))
                for row in rows:
                    lines.append("  " + " | ".join(str(v) for v in row))

        lines.append("")

    return "\n".join(lines)


def get_schema_dict() -> list[dict]:
    """Return structured schema info for the /schema API endpoint."""
    inspector = inspect(engine)
    tables = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

        tables.append({
            "table": table_name,
            "row_count": count,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "primary_key": bool(col.get("primary_key")),
                }
                for col in columns
            ],
        })

    return tables
