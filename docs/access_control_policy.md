# Access Control Policy

## Purpose

This policy defines how employees receive access to internal applications and what actions the IT Support Agent may perform automatically.

## Access Principles

Access is granted based on job role, department, manager approval, business justification, and application owner approval for sensitive systems.

Users should only receive the minimum access required for their work.

## Sensitive Applications

The following applications are considered sensitive:

- Finance Portal: contains payroll, budget, and vendor payment data.
- HR System: contains employee personal information.
- Admin Console: controls user permissions and system settings.
- Security Dashboard: contains security incidents and investigation data.

## Finance Portal Access

Finance Portal access requires a specific role.

- View reports requires FINANCE_VIEWER.
- Approve expenses requires FINANCE_APPROVER.
- Process payroll requires FINANCE_PAYROLL.
- Manage finance settings requires FINANCE_ADMIN.

Payroll access must be approved by the Finance Systems team.

## Automatic Actions Allowed

The IT Support Agent may automatically:

- Check whether a user has an application role.
- Create an access request.
- Create a support ticket.
- Send a mock notification to the responsible team.
- Write an audit log.

## Actions Not Allowed Automatically

The IT Support Agent must not automatically:

- Grant Finance Portal access.
- Grant admin access.
- Disable a user account.
- Delete user data.
- Change payroll information.
- Override approval workflows.

## Required Access Request Fields

An access request must include request ID, user ID, application name, requested role, business justification, priority, status, and created timestamp.

## Agent Instruction

If the user does not have the required access, the agent should create an access request, not directly grant the permission.
