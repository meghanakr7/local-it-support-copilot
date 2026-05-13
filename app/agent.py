from uuid import uuid4

from app.llm import LLMClient
from app.rag import search_docs, format_search_results
from app.tools import (
    analyze_email_text,
    check_application_status,
    check_device_health,
    check_software_approval,
    check_user_account_status,
    check_user_access_permission,
    check_vpn_status,
    classify_incident_priority,
    create_access_request,
    create_support_ticket,
    final_response_self_check,
    report_security_incident,
    request_software_installation,
    send_mock_email_notification,
    write_audit_log,
)


SYSTEM_PROMPT = """
You are a local enterprise IT support copilot.

Your job is to help employees resolve IT issues by using:
1. Retrieved internal IT documents.
2. Tool results from local mock enterprise systems.
3. Safe action policies.

Rules:
- Do not claim you granted access. You can only create an access request.
- Do not claim you installed software. You can only create a software installation request.
- Do not claim you sent a real email. You can only queue a mock notification.
- Do not claim you fixed production systems. You can only check mock system status and create records.
- Use evidence from retrieved documents and tool results.
- Be concise, professional, and explain what action was taken.
- If a support ticket, access request, software request, or security incident was created, include its ID.
"""


def _run_id() -> str:
    return f"RUN-{uuid4().hex[:8]}"


def _llm_final_answer(user_query: str, context: str, tool_results: dict) -> str:
    llm = LLMClient()

    user_prompt = f"""
User query:
{user_query}

Retrieved internal documents:
{context}

Tool results:
{tool_results}

Write a final response to the employee.

The response must include:
- Diagnosis
- Evidence
- Priority, if applicable
- Actions taken
- Ticket, request, incident, or notification IDs if created
- Clear next step
"""

    return llm.complete(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1
    )


def _complete_run(
    run_id: str,
    user_query: str,
    retrieved_documents: list[str],
    tools_called: list[str],
    final_answer: str,
    extra_tool_results: dict
) -> dict:
    audit_result = write_audit_log(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_decision=final_answer,
        status="completed"
    )

    tools_called_with_audit = tools_called + ["write_audit_log"]

    self_check_result = final_response_self_check(
        retrieved_documents=retrieved_documents,
        tools_called=tools_called_with_audit,
        final_answer=final_answer
    )

    return {
        "run_id": run_id,
        "user_query": user_query,
        "retrieved_documents": retrieved_documents,
        "tools_called": tools_called_with_audit,
        "tool_results": {
            **extra_tool_results,
            "audit": audit_result,
            "self_check": self_check_result,
        },
        "final_answer": final_answer
    }


def handle_finance_portal_access_issue(
    user_query: str,
    user_id: str = "u1001"
) -> dict:
    run_id = _run_id()

    rag_query = (
        "Finance portal access denied payroll role required access control "
        "incident priority escalation"
    )
    search_result = search_docs(rag_query, top_k=5)
    context = format_search_results(search_result)
    retrieved_documents = sorted(
        list({match["source"] for match in search_result["matches"]})
    )

    vpn_result = check_vpn_status()
    app_result = check_application_status("finance_portal")
    account_result = check_user_account_status(user_id)
    permission_result = check_user_access_permission(
        user_id=user_id,
        application_id="finance_portal",
        required_role="FINANCE_PAYROLL"
    )

    app_data = app_result["result"]
    permission_data = permission_result["result"]

    priority_result = classify_incident_priority(
        business_critical=app_data["business_critical"],
        blocks_user_work=True,
        multiple_users_affected=False,
        security_risk=False,
        time_sensitive=True
    )

    priority = priority_result["result"]["priority"]

    tools_called = [
        "search_docs",
        "check_vpn_status",
        "check_application_status",
        "check_user_account_status",
        "check_user_access_permission",
        "classify_incident_priority",
    ]

    access_request_result = None
    ticket_result = None
    email_result = None

    if not permission_data["has_required_role"]:
        access_request_result = create_access_request(
            user_id=user_id,
            application_id="finance_portal",
            requested_role="FINANCE_PAYROLL",
            business_justification="User needs payroll access before payroll deadline.",
            priority=priority
        )

        ticket_result = create_support_ticket(
            user_id=user_id,
            category="Finance Portal Access",
            priority=priority,
            summary="Finance portal payroll access blocked",
            details=(
                "User can reach the Finance Portal, account is active, "
                "but user does not have FINANCE_PAYROLL role required for payroll processing."
            ),
            assigned_team="Finance Systems"
        )

        email_result = send_mock_email_notification(
            to="finance-systems@example.local",
            subject=f"{priority} Finance Portal access request",
            body=(
                f"Access request {access_request_result['result']['request_id']} "
                f"and ticket {ticket_result['result']['ticket_id']} were created for user {user_id}."
            )
        )

        tools_called.extend(
            [
                "create_access_request",
                "create_support_ticket",
                "send_mock_email_notification",
            ]
        )

    tool_results = {
        "vpn": vpn_result,
        "application": app_result,
        "account": account_result,
        "permission": permission_result,
        "priority": priority_result,
        "access_request": access_request_result,
        "ticket": ticket_result,
        "email": email_result,
    }

    final_answer = _llm_final_answer(user_query, context, tool_results)

    return _complete_run(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_answer=final_answer,
        extra_tool_results=tool_results
    )


def handle_vpn_issue(
    user_query: str,
    user_id: str = "u1001",
    use_degraded_demo: bool = True
) -> dict:
    run_id = _run_id()

    rag_query = "VPN troubleshooting degraded service escalation urgent access"
    search_result = search_docs(rag_query, top_k=4)
    context = format_search_results(search_result)
    retrieved_documents = sorted(
        list({match["source"] for match in search_result["matches"]})
    )

    vpn_result = check_vpn_status(use_degraded_demo=use_degraded_demo)
    account_result = check_user_account_status(user_id)

    vpn_status = vpn_result["result"]["status"]
    affected_users = vpn_result["result"]["affected_users"]

    priority_result = classify_incident_priority(
        business_critical=True,
        blocks_user_work=True,
        multiple_users_affected=affected_users > 1,
        security_risk=False,
        time_sensitive=True
    )

    priority = priority_result["result"]["priority"]

    tools_called = [
        "search_docs",
        "check_vpn_status",
        "check_user_account_status",
        "classify_incident_priority",
    ]

    ticket_result = None
    email_result = None

    if vpn_status in {"degraded", "down", "unknown"}:
        ticket_result = create_support_ticket(
            user_id=user_id,
            category="VPN Connectivity",
            priority=priority,
            summary="VPN service issue affecting remote access",
            details=(
                f"VPN status is {vpn_status}. "
                f"Affected users: {affected_users}. "
                "User needs urgent internal access."
            ),
            assigned_team="Network Operations"
        )

        email_result = send_mock_email_notification(
            to="network-operations@example.local",
            subject=f"{priority} VPN connectivity issue",
            body=(
                f"Ticket {ticket_result['result']['ticket_id']} created. "
                f"VPN status: {vpn_status}. Affected users: {affected_users}."
            )
        )

        tools_called.extend(["create_support_ticket", "send_mock_email_notification"])

    tool_results = {
        "vpn": vpn_result,
        "account": account_result,
        "priority": priority_result,
        "ticket": ticket_result,
        "email": email_result,
    }

    final_answer = _llm_final_answer(user_query, context, tool_results)

    return _complete_run(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_answer=final_answer,
        extra_tool_results=tool_results
    )


def handle_software_installation_request(
    user_query: str,
    user_id: str = "u1002",
    software_name: str = "Docker Desktop"
) -> dict:
    run_id = _run_id()

    rag_query = "software installation policy approved software Docker Desktop request"
    search_result = search_docs(rag_query, top_k=4)
    context = format_search_results(search_result)
    retrieved_documents = sorted(
        list({match["source"] for match in search_result["matches"]})
    )

    account_result = check_user_account_status(user_id)
    approval_result = check_software_approval(software_name, user_id)

    account_data = account_result["result"]
    approval_data = approval_result["result"]

    priority_result = classify_incident_priority(
        business_critical=False,
        blocks_user_work=True,
        multiple_users_affected=False,
        security_risk=False,
        time_sensitive=False
    )

    priority = priority_result["result"]["priority"]

    tools_called = [
        "search_docs",
        "check_user_account_status",
        "check_software_approval",
        "classify_incident_priority",
    ]

    software_request_result = None
    ticket_result = None
    email_result = None

    if approval_data["approved"] and approval_data["allowed_for_user"]:
        software_request_result = request_software_installation(
            user_id=user_id,
            software_name=software_name,
            device_id=account_data["device_id"],
            business_justification="User needs software for development work.",
            approval_status="pre_approved"
        )

        email_result = send_mock_email_notification(
            to="it-service-desk@example.local",
            subject=f"Software installation request: {software_name}",
            body=(
                f"Software request {software_request_result['result']['request_id']} "
                f"created for user {user_id}."
            )
        )

        tools_called.extend(
            [
                "request_software_installation",
                "send_mock_email_notification",
            ]
        )
    else:
        ticket_result = create_support_ticket(
            user_id=user_id,
            category="Software Approval",
            priority=priority,
            summary=f"Manual review required for {software_name}",
            details=(
                f"Software approval check failed or user role is not allowed. "
                f"Software: {software_name}."
            ),
            assigned_team="IT Service Desk"
        )

        tools_called.append("create_support_ticket")

    tool_results = {
        "account": account_result,
        "approval": approval_result,
        "priority": priority_result,
        "software_request": software_request_result,
        "ticket": ticket_result,
        "email": email_result,
    }

    final_answer = _llm_final_answer(user_query, context, tool_results)

    return _complete_run(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_answer=final_answer,
        extra_tool_results=tool_results
    )


def handle_phishing_report(
    user_query: str,
    user_id: str = "u1001"
) -> dict:
    run_id = _run_id()

    rag_query = "phishing suspicious email reset password urgent click here security incident"
    search_result = search_docs(rag_query, top_k=4)
    context = format_search_results(search_result)
    retrieved_documents = sorted(
        list({match["source"] for match in search_result["matches"]})
    )

    analysis_result = analyze_email_text(user_query)
    risk = analysis_result["result"]["risk"]
    indicators = analysis_result["result"]["matched_indicators"]

    priority_result = classify_incident_priority(
        business_critical=False,
        blocks_user_work=False,
        multiple_users_affected=False,
        security_risk=risk in {"medium", "high"},
        time_sensitive=True
    )

    priority = priority_result["result"]["priority"]

    tools_called = [
        "search_docs",
        "analyze_email_text",
        "classify_incident_priority",
    ]

    incident_result = None
    email_result = None

    if risk in {"medium", "high"}:
        incident_result = report_security_incident(
            user_id=user_id,
            risk=risk,
            summary="Suspicious email reported by user",
            indicators=indicators
        )

        email_result = send_mock_email_notification(
            to="security-operations@example.local",
            subject=f"{priority} phishing report",
            body=(
                f"Security incident {incident_result['result']['incident_id']} "
                f"created. Risk: {risk}. Indicators: {', '.join(indicators)}."
            )
        )

        tools_called.extend(
            [
                "report_security_incident",
                "send_mock_email_notification",
            ]
        )

    tool_results = {
        "analysis": analysis_result,
        "priority": priority_result,
        "incident": incident_result,
        "email": email_result,
    }

    final_answer = _llm_final_answer(user_query, context, tool_results)

    return _complete_run(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_answer=final_answer,
        extra_tool_results=tool_results
    )


def handle_laptop_performance_issue(
    user_query: str,
    user_id: str = "u1001"
) -> dict:
    run_id = _run_id()

    rag_query = "laptop slow freezing meetings CPU disk battery performance troubleshooting"
    search_result = search_docs(rag_query, top_k=4)
    context = format_search_results(search_result)
    retrieved_documents = sorted(
        list({match["source"] for match in search_result["matches"]})
    )

    account_result = check_user_account_status(user_id)
    device_result = check_device_health(user_id)
    device_data = device_result["result"]

    blocks_work = (
        device_data["cpu_usage"] > 90
        or device_data["disk_free_gb"] < 5
        or device_data["battery_health"] == "poor"
    )

    priority_result = classify_incident_priority(
        business_critical=False,
        blocks_user_work=blocks_work,
        multiple_users_affected=False,
        security_risk=False,
        time_sensitive=True
    )

    priority = priority_result["result"]["priority"]

    tools_called = [
        "search_docs",
        "check_user_account_status",
        "check_device_health",
        "classify_incident_priority",
    ]

    ticket_result = None

    if blocks_work:
        ticket_result = create_support_ticket(
            user_id=user_id,
            category="Laptop Performance",
            priority=priority,
            summary="Laptop performance issue requires endpoint review",
            details=(
                f"Device health indicates CPU {device_data['cpu_usage']}%, "
                f"memory {device_data['memory_usage']}%, "
                f"disk free {device_data['disk_free_gb']} GB, "
                f"battery health {device_data['battery_health']}."
            ),
            assigned_team="Endpoint Support"
        )

        tools_called.append("create_support_ticket")

    tool_results = {
        "account": account_result,
        "device": device_result,
        "priority": priority_result,
        "ticket": ticket_result,
    }

    final_answer = _llm_final_answer(user_query, context, tool_results)

    return _complete_run(
        run_id=run_id,
        user_query=user_query,
        retrieved_documents=retrieved_documents,
        tools_called=tools_called,
        final_answer=final_answer,
        extra_tool_results=tool_results
    )


def route_user_query(user_query: str) -> str:
    lowered = user_query.lower()

    if "finance" in lowered or "payroll" in lowered:
        return "finance_portal_access"

    if "vpn" in lowered:
        return "vpn_issue"

    if "install" in lowered or "software" in lowered or "docker" in lowered:
        return "software_installation"

    if "phishing" in lowered or "suspicious email" in lowered or "click here" in lowered or "reset password" in lowered:
        return "phishing_report"

    if "laptop" in lowered or "slow" in lowered or "freezing" in lowered:
        return "laptop_performance"

    return "finance_portal_access"


def handle_user_query(user_query: str) -> dict:
    route = route_user_query(user_query)

    if route == "finance_portal_access":
        return handle_finance_portal_access_issue(user_query)

    if route == "vpn_issue":
        return handle_vpn_issue(user_query)

    if route == "software_installation":
        return handle_software_installation_request(user_query)

    if route == "phishing_report":
        return handle_phishing_report(user_query)

    if route == "laptop_performance":
        return handle_laptop_performance_issue(user_query)

    return handle_finance_portal_access_issue(user_query)