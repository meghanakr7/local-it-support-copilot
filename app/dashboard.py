import json
from typing import Any

import pandas as pd
import streamlit as st

try:
    from app.config import settings
    from app.agent import handle_user_query
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(PROJECT_ROOT))

    from app.config import settings
    from app.agent import handle_user_query


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


def show_chatbot() -> None:
    st.subheader("IT Support Chatbot")
    st.caption(
        "Ask an IT support question. The agent will search internal docs, call tools, "
        "create local actions, and return an explainable answer."
    )

    example_queries = [
        "I cannot access the finance portal from home. VPN is connected, but the finance site says access denied. I need it before payroll closes today.",
        "My VPN is not connecting. I already restarted my laptop and I need urgent access to internal systems.",
        "Can you install Docker Desktop on my laptop? I need it for development work.",
        "I received an email saying my password will expire today. It says urgent action required and asks me to click here to reset password. Is this safe?",
        "My laptop is very slow and keeps freezing during meetings.",
    ]

    selected_example = st.selectbox(
        "Try a demo query",
        [""] + example_queries,
        index=0,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        use_example = st.button("Use selected example", use_container_width=True)

    with col2:
        clear_chat = st.button("Clear chat", use_container_width=True)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I am your Local Enterprise IT Support Copilot. "
                    "Ask me about VPN, Finance Portal access, software requests, phishing emails, or laptop performance."
                ),
            }
        ]

    if clear_chat:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Chat cleared. What IT issue can I help you with?",
            }
        ]
        st.rerun()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("metadata"):
                with st.expander("Agent trace"):
                    st.json(message["metadata"])

    prompt = st.chat_input("Describe your IT issue...")

    if use_example and selected_example:
        prompt = selected_example

    if prompt:
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent is searching docs and running tools..."):
                try:
                    result = handle_user_query(prompt)

                    final_answer = result.get(
                        "final_answer",
                        "I processed the request, but no final answer was returned.",
                    )

                    metadata = {
                        "run_id": result.get("run_id"),
                        "retrieved_documents": result.get("retrieved_documents", []),
                        "tools_called": result.get("tools_called", []),
                        "tool_results": result.get("tool_results", []),
                    }

                    st.markdown(final_answer)

                    with st.expander("Agent trace"):
                        st.json(metadata)

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": final_answer,
                            "metadata": metadata,
                        }
                    )

                    st.success(
                        "Action completed. Refresh the dashboard tabs to see updated tickets, requests, emails, and audit logs."
                    )

                except Exception as exc:
                    error_message = (
                        "Sorry, the agent failed while processing this request. "
                        f"Error: `{exc}`"
                    )
                    st.error(error_message)

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                        }
                    )


def show_knowledge_base() -> None:
    st.subheader("Knowledge Base Documents")

    docs = sorted(settings.docs_dir.glob("*.md"))

    if not docs:
        st.warning("No documents found.")
    else:
        for doc in docs:
            with st.expander(doc.name):
                st.markdown(doc.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(
        page_title="Local IT Support Copilot Dashboard",
        page_icon="🛠️",
        layout="wide",
    )

    st.title("Local Enterprise IT Support Copilot")
    st.caption(
        "A RAG + tool-use IT support agent with mock enterprise actions, local JSON systems, and audit logging."
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Tickets", count_records("tickets.json"))
    col2.metric("Access Requests", count_records("access_requests.json"))
    col3.metric("Software Requests", count_records("software_requests.json"))
    col4.metric("Security Incidents", count_records("security_incidents.json"))
    col5.metric("Mock Emails", count_records("email_outbox.json"))
    col6.metric("Audit Logs", count_records("audit_logs.json"))

    st.divider()

    tabs = st.tabs(
        [
            "IT Support Chatbot",
            "Support Tickets",
            "Access Requests",
            "Software Requests",
            "Security Incidents",
            "Mock Email Outbox",
            "Audit Logs",
            "Knowledge Base",
        ]
    )

    with tabs[0]:
        show_chatbot()

    with tabs[1]:
        show_table("Support Tickets", "tickets.json")

    with tabs[2]:
        show_table("Access Requests", "access_requests.json")

    with tabs[3]:
        show_table("Software Installation Requests", "software_requests.json")

    with tabs[4]:
        show_table("Security Incidents", "security_incidents.json")

    with tabs[5]:
        show_table("Mock Email Outbox", "email_outbox.json")

    with tabs[6]:
        show_table("Audit Logs", "audit_logs.json")

    with tabs[7]:
        show_knowledge_base()


if __name__ == "__main__":
    main()
