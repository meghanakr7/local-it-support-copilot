from rich import print
from rich.panel import Panel

from app.rag import build_index
from app.agent import handle_finance_portal_access_issue


def main() -> None:
    print("[bold cyan]Building local document index...[/bold cyan]")
    index_result = build_index(reset=True)
    print(index_result)

    user_query = (
        "I cannot access the finance portal from home. "
        "VPN is connected, but the finance site says access denied. "
        "I need it before payroll closes today."
    )

    print("\n[bold cyan]Running IT Support Copilot demo...[/bold cyan]")
    print(Panel(user_query, title="User Query"))

    result = handle_finance_portal_access_issue(user_query=user_query)

    print("\n[bold green]Final Agent Response[/bold green]")
    print(Panel(result["final_answer"], title="Agent"))

    print("\n[bold cyan]Created Records[/bold cyan]")

    access_request = result["tool_results"]["access_request"]
    ticket = result["tool_results"]["ticket"]
    email = result["tool_results"]["email"]
    audit = result["tool_results"]["audit"]
    self_check = result["tool_results"]["self_check"]

    print({
        "access_request": access_request["result"] if access_request else None,
        "ticket": ticket["result"] if ticket else None,
        "mock_email": email["result"] if email else None,
        "audit_log": audit["result"],
        "self_check": self_check["result"],
    })


if __name__ == "__main__":
    main()