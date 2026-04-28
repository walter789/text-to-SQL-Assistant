import requests
import pandas as pd
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Text-to-SQL Assistant", page_icon="🔍", layout="wide")

st.title("🔍 Text-to-SQL Analytics Assistant")
st.caption("Ask questions in plain English — get SQL + data-driven insights powered by Claude")

# ── Sidebar: Schema Explorer + History ────────────────────────────────────────
with st.sidebar:
    st.header("📋 Database Schema")
    try:
        schema_resp = requests.get(f"{API_URL}/schema", timeout=5)
        if schema_resp.ok:
            for table in schema_resp.json()["tables"]:
                with st.expander(f"📄 {table['table']}  ({table['row_count']} rows)"):
                    for col in table["columns"]:
                        pk = " 🔑" if col["primary_key"] else ""
                        st.markdown(f"`{col['name']}` — {col['type']}{pk}")
        else:
            st.warning("Could not load schema.")
    except Exception:
        st.warning("API not reachable. Start the backend first.")

    st.divider()

    st.header("🕑 Recent Queries")
    try:
        hist_resp = requests.get(f"{API_URL}/history", timeout=5)
        if hist_resp.ok:
            history = hist_resp.json()["history"]
            if not history:
                st.info("No queries yet.")
            for entry in history[:5]:
                with st.expander(entry["question"][:60] + "…"):
                    st.code(entry["sql_query"], language="sql")
                    st.markdown(f"**Confidence:** {entry['confidence']:.0%}")
        else:
            st.info("No history available.")
    except Exception:
        pass

# ── Main Panel ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input(
        "Ask a question about the Northwind data:",
        placeholder='e.g. "Which product category had the highest total revenue?"',
    )
with col2:
    max_rows = st.number_input("Max rows", min_value=1, max_value=500, value=100)

example_questions = [
    "Show me the top 5 customers by total order value",
    "Which employee processed the most orders?",
    "What is the average order value per country?",
    "Which products are discontinued?",
    "List all categories and how many products each has",
]

st.markdown("**Quick examples:**")
cols = st.columns(len(example_questions))
for i, q in enumerate(example_questions):
    if cols[i].button(q[:35] + "…", key=f"ex_{i}"):
        question = q

if st.button("🚀 Run Query", type="primary", disabled=not question):
    with st.spinner("Generating SQL and fetching insights…"):
        try:
            resp = requests.post(
                f"{API_URL}/query",
                json={"question": question, "max_rows": max_rows},
                timeout=60,
            )
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend. Run: `uvicorn app.main:app --reload`")
            st.stop()

    if resp.ok:
        data = resp.json()

        st.success("Query completed successfully!")

        # Confidence + retries badges
        badge_col1, badge_col2, badge_col3 = st.columns(3)
        badge_col1.metric("Confidence", f"{data['confidence']:.0%}")
        badge_col2.metric("Rows Returned", len(data["result_data"]))
        badge_col3.metric("Self-Corrections Used", data["retries_used"])

        st.divider()

        # Generated SQL
        st.subheader("🗄️ Generated SQL")
        st.code(data["sql_query"], language="sql")

        # Answer
        st.subheader("💬 Answer")
        st.markdown(data["natural_language_answer"].replace("$", r"\$"))

        # Key insights
        st.subheader("💡 Key Insights")
        for insight in data["key_insights"]:
            st.markdown(f"• {insight.replace('$', r'\$')}")

        # Results table
        st.subheader("📊 Query Results")
        if data["result_data"]:
            df = pd.DataFrame(data["result_data"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Query returned no rows.")

    else:
        error = resp.json().get("detail", {})
        st.error(f"**{error.get('error_type', 'Error')}:** {error.get('message', 'Unknown error')}")
        if error.get("failed_query"):
            st.code(error["failed_query"], language="sql")
