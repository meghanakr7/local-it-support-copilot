import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from app.config import settings


st.set_page_config(
    page_title="Local IT Support Copilot Dashboard",
    page_icon="🛠️",
    layout="wide",
)


def read_json_file(filename: str) -> Any:
    file_path = settings.mock_data_dir / filename

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def show_table(title: str, filename: str) -> None:
    st.subheader(title)

    data = read_json_file(filename)

    if not data:
        st.info(f"No records found in {filename}.")
        return

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def count_records(filename: str) -> int:
    data = read_json_file(filename)

    if isinstance(data, list):
        return len(data)

    if isinstance(data, dict):
        return len(data.keys())

    return 0


def main() -> None:
    st.title("Local Enterprise IT Support Copilot")
    st.caption(
        "A fully local-style RAG + tool-use IT support agent with mock enterprise actions."
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Tickets", count_records("tickets.json"))
    col2.metric("Access Requests", count_records("access_requests.json"))
    col3.metric("Software Requests", count_records("software_requests.json"))
    col4.metric("Security Incidents", count_records("security_incidents.json"))
    col5.metric("Mock Emails", count_records("email_outbox.json"))

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Support Tickets",
            "Access Requests",
            "Software Requests",
            "Security Incidents",
            "Mock Email Outbox",
            "Audit Logs",
        ]
    )

    with tab1:
        show_table("Support Tickets", "tickets.json")

    with tab2:
        show_table("Access Requests", "access_requests.json")

    with tab3:
        show_table("Software Installation Requests", "software_requests.json")

    with tab4:
        show_table("Security Incidents", "security_incidents.json")

    with tab5:
        show_table("Mock Email Outbox", "email_outbox.json")

    with tab6:
        show_table("Audit Logs", "audit_logs.json")

    st.divider()

    st.subheader("Knowledge Base Documents")

    docs = sorted(settings.docs_dir.glob("*.md"))
    if not docs:
        st.warning("No documents found.")
    else:
        for doc in docs:
            with st.expander(doc.name):
                st.markdown(doc.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()