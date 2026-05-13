from pathlib import Path
from datetime import datetime

from app.agent import handle_user_query


DEMO_QUERIES = [
    {
        "title": "Finance Portal Access Issue",
        "query": (
            "I cannot access the finance portal from home. VPN is connected, "
            "but the finance site says access denied. I need it before payroll closes today."
        ),
    },
    {
        "title": "VPN Issue",
        "query": (
            "My VPN is not connecting. I already restarted my laptop and I need urgent access "
            "to internal systems."
        ),
    },
    {
        "title": "Software Installation Request",
        "query": (
            "Can you install Docker Desktop on my laptop? I need it for development work."
        ),
    },
    {
        "title": "Phishing Email Report",
        "query": (
            "I received an email saying my password will expire today. It says urgent action required "
            "and asks me to click here to reset password. Is this safe?"
        ),
    },
    {
        "title": "Slow Laptop Diagnosis",
        "query": (
            "My laptop is very slow and keeps freezing during meetings."
        ),
    },
]


def format_demo_result(index: int, title: str, query: str, result: dict) -> str:
    return f"""
================================================================================
DEMO {index}: {title}
================================================================================

USER QUERY:
{query}

RUN ID:
{result.get("run_id")}

RETRIEVED DOCUMENTS:
{result.get("retrieved_documents", [])}

TOOLS CALLED:
{result.get("tools_called", [])}

FINAL ANSWER:
{result.get("final_answer")}

RAW TOOL RESULTS:
{result.get("tool_results", [])}
"""


def main() -> None:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"demo_run_{timestamp}.md"

    output_parts = [
        "# Local Enterprise IT Support Copilot Demo Run\n",
        f"Generated at: {datetime.now().isoformat()}\n",
    ]

    for index, item in enumerate(DEMO_QUERIES, start=1):
        print("=" * 80)
        print(f"DEMO {index}: {item['title']}")
        print(item["query"])

        result = handle_user_query(item["query"])

        formatted = format_demo_result(
            index=index,
            title=item["title"],
            query=item["query"],
            result=result,
        )

        print(formatted)
        output_parts.append(formatted)

    log_path.write_text("\n".join(output_parts), encoding="utf-8")

    print("=" * 80)
    print(f"Demo log saved to: {log_path}")


if __name__ == "__main__":
    main()
