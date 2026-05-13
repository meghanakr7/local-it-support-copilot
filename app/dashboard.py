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
    st.dataframe(df, width="stretch")


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
        "Ask an IT support question. The agent can search internal docs, call tools, "
        "create mock actions, and return an explainable answer."
    )

    demo_queries = [
        "",
        "I cannot connect to VPN from home. Please help me troubleshoot.",
        "I need access to the Finance Portal for payroll processing.",
        "I received a suspicious password reset email from an unknown sender. Please investigate.",
        "Can you install Docker Desktop on my laptop? I need it for development work.",
        "My laptop is running very slowly after the latest update.",
    ]

    selected_example = st.selectbox("Try a demo query", demo_queries)

    col1, col2 = st.columns([1, 1])

    with col1:
        use_example = st.button(
            "Use selected example",
            width="stretch",
            disabled=not selected_example,
        )

    with col2:
        clear_chat = st.button("Clear chat", width="stretch")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I am your Local Enterprise IT Support Copilot. "
                    "I can help with VPN issues, Finance Portal access, software installation, "
                    "suspicious emails, laptop performance, and support ticket creation."
                ),
                "trace": None,
            }
        ]

    if clear_chat:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I am your Local Enterprise IT Support Copilot. "
                    "I can help with VPN issues, Finance Portal access, software installation, "
                    "suspicious emails, laptop performance, and support ticket creation."
                ),
                "trace": None,
            }
        ]
        st.rerun()

    if use_example and selected_example:
        st.session_state.pending_prompt = selected_example
        st.rerun()

    st.divider()

    # Always render messages BEFORE chat_input
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            trace = msg.get("trace")
            if trace:
                with st.expander("Agent trace"):
                    st.json(trace)

    prompt = st.chat_input("Describe your IT issue...")

    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
                "trace": None,
            }
        )

        try:
            with st.spinner("Thinking..."):
                result = handle_user_query(prompt)

            final_answer = result.get(
                "final_answer",
                "I processed your request, but no final answer was generated.",
            )

            trace = {
                "run_id": result.get("run_id"),
                "intent": result.get("intent"),
                "retrieved_documents": result.get("retrieved_documents", []),
                "tools_called": result.get("tools_called", []),
                "actions_created": result.get("actions_created", []),
            }

            # Only show trace when something meaningful happened
            has_trace = bool(
                trace["retrieved_documents"]
                or trace["tools_called"]
                or trace["actions_created"]
            )

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": final_answer,
                    "trace": trace if has_trace else None,
                }
            )

        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            print("\n===== CHATBOT ERROR TRACEBACK =====")
            print(tb)
            print("===== END CHATBOT ERROR TRACEBACK =====\n")

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Sorry, I could not process that request. "
                        "Please try again or describe the issue more specifically."
                    ),
                    "trace": {"error": str(e)},
                }
            )

        st.rerun()

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
