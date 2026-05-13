import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings


def _path(filename: str) -> Path:
    return settings.mock_data_dir / filename


def _read_json(filename: str) -> Any:
    file_path = _path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"Missing mock data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(filename: str, data: Any) -> None:
    file_path = _path(filename)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _next_id(prefix: str, existing_items: list[dict[str, Any]]) -> str:
    return f"{prefix}-{len(existing_items) + 1001}"


def check_vpn_status(use_degraded_demo: bool = False) -> dict[str, Any]:
    services = _read_json("services.json")
    key = "vpn_degraded_demo" if use_degraded_demo else "vpn"

    service = services.get(key)
    if not service:
        return {
            "status": "error",
            "message": f"VPN service key '{key}' not found"
        }

    return {
        "tool": "check_vpn_status",
        "result": service
    }


def check_application_status(application_id: str) -> dict[str, Any]:
    applications = _read_json("applications.json")
    app = applications.get(application_id)

    if not app:
        return {
            "tool": "check_application_status",
            "status": "error",
            "message": f"Application '{application_id}' not found"
        }

    return {
        "tool": "check_application_status",
        "result": app
    }


def check_user_account_status(user_id: str) -> dict[str, Any]:
    users = _read_json("users.json")
    user = users.get(user_id)

    if not user:
        return {
            "tool": "check_user_account_status",
            "status": "error",
            "message": f"User '{user_id}' not found"
        }

    return {
        "tool": "check_user_account_status",
        "result": {
            "user_id": user_id,
            "name": user["name"],
            "department": user["department"],
            "role": user["role"],
            "account_status": user["account_status"],
            "device_id": user["device_id"]
        }
    }


def check_user_access_permission(
    user_id: str,
    application_id: str,
    required_role: str
) -> dict[str, Any]:
    users = _read_json("users.json")
    user = users.get(user_id)

    if not user:
        return {
            "tool": "check_user_access_permission",
            "status": "error",
            "message": f"User '{user_id}' not found"
        }

    user_roles = user.get("application_roles", {}).get(application_id, [])
    has_required_role = required_role in user_roles

    return {
        "tool": "check_user_access_permission",
        "result": {
            "user_id": user_id,
            "application_id": application_id,
            "required_role": required_role,
            "user_roles": user_roles,
            "has_required_role": has_required_role
        }
    }


def check_software_approval(software_name: str, user_id: str) -> dict[str, Any]:
    users = _read_json("users.json")
    software_catalog = _read_json("software_catalog.json")

    user = users.get(user_id)
    if not user:
        return {
            "tool": "check_software_approval",
            "status": "error",
            "message": f"User '{user_id}' not found"
        }

    software = software_catalog.get(software_name)
    if not software:
        return {
            "tool": "check_software_approval",
            "result": {
                "software_name": software_name,
                "approved": False,
                "allowed_for_user": False,
                "reason": "Software is not listed in the approved catalog"
            }
        }

    allowed_for_user = user["role"] in software.get("allowed_roles", [])

    return {
        "tool": "check_software_approval",
        "result": {
            "software_name": software_name,
            "user_id": user_id,
            "user_role": user["role"],
            "approved": software["approved"],
            "allowed_for_user": allowed_for_user,
            "requires_manual_approval": software["requires_manual_approval"]
        }
    }


def check_device_health(user_id: str) -> dict[str, Any]:
    users = _read_json("users.json")
    devices = _read_json("devices.json")

    user = users.get(user_id)
    if not user:
        return {
            "tool": "check_device_health",
            "status": "error",
            "message": f"User '{user_id}' not found"
        }

    device_id = user["device_id"]
    device = devices.get(device_id)

    if not device:
        return {
            "tool": "check_device_health",
            "status": "error",
            "message": f"Device '{device_id}' not found"
        }

    return {
        "tool": "check_device_health",
        "result": {
            "device_id": device_id,
            **device
        }
    }


def analyze_email_text(email_text: str) -> dict[str, Any]:
    suspicious_terms = [
        "urgent",
        "reset password",
        "verify your account",
        "click here",
        "payment required",
        "account locked",
        "gift card",
        "wire transfer",
        "password will expire"
    ]

    lowered = email_text.lower()
    matched = [term for term in suspicious_terms if term in lowered]

    if len(matched) >= 3:
        risk = "high"
    elif len(matched) >= 1:
        risk = "medium"
    else:
        risk = "low"

    return {
        "tool": "analyze_email_text",
        "result": {
            "risk": risk,
            "matched_indicators": matched
        }
    }


def classify_incident_priority(
    business_critical: bool,
    blocks_user_work: bool,
    multiple_users_affected: bool = False,
    security_risk: bool = False,
    time_sensitive: bool = False
) -> dict[str, Any]:
    if multiple_users_affected and (business_critical or security_risk):
        priority = "P1"
        reason = "Critical issue affecting multiple users or security operations"
    elif business_critical and blocks_user_work:
        priority = "P2"
        reason = "Single user is blocked from business-critical work"
    elif security_risk:
        priority = "P2"
        reason = "Security risk requires same-day response"
    elif blocks_user_work or time_sensitive:
        priority = "P3"
        reason = "User work is impacted but not classified as business-critical"
    else:
        priority = "P4"
        reason = "General or low-impact request"

    return {
        "tool": "classify_incident_priority",
        "result": {
            "priority": priority,
            "reason": reason
        }
    }


def create_support_ticket(
    user_id: str,
    category: str,
    priority: str,
    summary: str,
    details: str,
    assigned_team: str
) -> dict[str, Any]:
    tickets = _read_json("tickets.json")
    ticket_id = _next_id("IT", tickets)

    ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "category": category,
        "priority": priority,
        "summary": summary,
        "details": details,
        "assigned_team": assigned_team,
        "status": "open",
        "created_at": _now()
    }

    tickets.append(ticket)
    _write_json("tickets.json", tickets)

    return {
        "tool": "create_support_ticket",
        "result": ticket
    }


def create_access_request(
    user_id: str,
    application_id: str,
    requested_role: str,
    business_justification: str,
    priority: str
) -> dict[str, Any]:
    access_requests = _read_json("access_requests.json")
    request_id = _next_id("AR", access_requests)

    request = {
        "request_id": request_id,
        "user_id": user_id,
        "application_id": application_id,
        "requested_role": requested_role,
        "business_justification": business_justification,
        "priority": priority,
        "status": "pending_approval",
        "created_at": _now()
    }

    access_requests.append(request)
    _write_json("access_requests.json", access_requests)

    return {
        "tool": "create_access_request",
        "result": request
    }


def request_software_installation(
    user_id: str,
    software_name: str,
    device_id: str,
    business_justification: str,
    approval_status: str
) -> dict[str, Any]:
    software_requests = _read_json("software_requests.json")
    request_id = _next_id("SW", software_requests)

    request = {
        "request_id": request_id,
        "user_id": user_id,
        "software_name": software_name,
        "device_id": device_id,
        "business_justification": business_justification,
        "approval_status": approval_status,
        "status": "requested",
        "created_at": _now()
    }

    software_requests.append(request)
    _write_json("software_requests.json", software_requests)

    return {
        "tool": "request_software_installation",
        "result": request
    }


def report_security_incident(
    user_id: str,
    risk: str,
    summary: str,
    indicators: list[str]
) -> dict[str, Any]:
    incidents = _read_json("security_incidents.json")
    incident_id = _next_id("SEC", incidents)

    incident = {
        "incident_id": incident_id,
        "user_id": user_id,
        "risk": risk,
        "summary": summary,
        "indicators": indicators,
        "status": "reported",
        "created_at": _now()
    }

    incidents.append(incident)
    _write_json("security_incidents.json", incidents)

    return {
        "tool": "report_security_incident",
        "result": incident
    }


def send_mock_email_notification(
    to: str,
    subject: str,
    body: str
) -> dict[str, Any]:
    emails = _read_json("email_outbox.json")
    email_id = _next_id("EMAIL", emails)

    email = {
        "email_id": email_id,
        "to": to,
        "subject": subject,
        "body": body,
        "status": "queued_mock",
        "created_at": _now()
    }

    emails.append(email)
    _write_json("email_outbox.json", emails)

    return {
        "tool": "send_mock_email_notification",
        "result": email
    }


def write_audit_log(
    run_id: str,
    user_query: str,
    retrieved_documents: list[str],
    tools_called: list[str],
    final_decision: str,
    status: str
) -> dict[str, Any]:
    logs = _read_json("audit_logs.json")
    log_id = _next_id("AUDIT", logs)

    log = {
        "log_id": log_id,
        "run_id": run_id,
        "user_query": user_query,
        "retrieved_documents": retrieved_documents,
        "tools_called": tools_called,
        "final_decision": final_decision,
        "status": status,
        "created_at": _now()
    }

    logs.append(log)
    _write_json("audit_logs.json", logs)

    return {
        "tool": "write_audit_log",
        "result": log
    }


def validate_action_allowed(action_name: str) -> dict[str, Any]:
    safe_actions = {
        "check_vpn_status",
        "check_application_status",
        "check_user_account_status",
        "check_user_access_permission",
        "check_software_approval",
        "check_device_health",
        "create_support_ticket",
        "create_access_request",
        "request_software_installation",
        "report_security_incident",
        "send_mock_email_notification",
        "write_audit_log"
    }

    restricted_actions = {
        "grant_finance_role",
        "reset_password",
        "unlock_account",
        "delete_user_data",
        "change_payroll_data",
        "disable_account"
    }

    if action_name in safe_actions:
        allowed = True
        reason = "Action is allowed by the IT Action Safety Policy"
    elif action_name in restricted_actions:
        allowed = False
        reason = "Action is restricted and requires human approval"
    else:
        allowed = False
        reason = "Action is unknown and cannot be executed automatically"

    return {
        "tool": "validate_action_allowed",
        "result": {
            "action_name": action_name,
            "allowed": allowed,
            "reason": reason
        }
    }


def final_response_self_check(
    retrieved_documents: list[str],
    tools_called: list[str],
    final_answer: str
) -> dict[str, Any]:
    checks = {
        "has_retrieved_documents": len(retrieved_documents) > 0,
        "has_tool_calls": len(tools_called) > 0,
        "has_final_answer": len(final_answer.strip()) > 0,
        "mentions_ticket_or_request_when_action_taken": (
            ("create_support_ticket" not in tools_called and "create_access_request" not in tools_called)
            or ("IT-" in final_answer or "AR-" in final_answer)
        )
    }

    passed = all(checks.values())

    return {
        "tool": "final_response_self_check",
        "result": {
            "passed": passed,
            "checks": checks
        }
    }